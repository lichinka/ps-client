import time
import psutil
import threading

from collections import namedtuple

from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base ( )
class DiskActivityEntity (Base):
    """
    ORM entity representing this computer's disk activity.-
    """
    __tablename__ = 'disk'

    #
    # Identity column
    #
    id = Column (Integer,
                 primary_key=True)
    #
    # time of measurement, in seconds since the epoch
    #
    time = Column (Float,
                   nullable=False,
                   unique=True)
    #
    # disk read activity, expressed in KB per second
    #
    read = Column (Float,
                   nullable=False)
    #
    # disk write activity, expressed in KB per second
    #
    write = Column (Float,
                    nullable=False)

    def __init__ (self, named_params=None):
        """
        Constructs a new entity, taking the field values from the
        named tuple received as parameter.-
        """
        if named_params is not None:
            self.time = float (named_params.time)
            self.read = float (named_params.read)
            self.write = float (named_params.write)


    def __repr__ (self):
        return "<Disk (%.3f, %.3f, %.3f)>" % (self.time,
                                              self.read,
                                              self.write)



class DiskActivity (object):
    """
    A class to gather disk-activity statistics.-
    """
    #
    # named tuple type to move data around the class
    #
    _Data = namedtuple ('Data',
                        'time read write')

    def _collect (self):
        """
        Collects disk(s) activity, using the PSUtil library.-
        """
        when = time.time ( )
        my_io_counters = psutil.disk_io_counters ( )
        ret_value = DiskActivity._Data (when,
                                        my_io_counters.read_bytes,
                                        my_io_counters.write_bytes)
        return ret_value


    def __init__ (self):
        self.io_counters = self._collect ( )
        self.last_read_delta = None
        self.last_write_delta = None


    def measure (self):
        """
        Returns a named tuple containing disk read and write activity.
        The result is as follows:

            time    is the time of the measurement, in seconds since
                    the epoch;
            read    is the disk read activity, expressed in KB/second;
            write   is the disk write activity, expressed in KB/second.-

        """
        my_io_counters = self._collect ( )
        #
        # prevent miscalculation of measurements that are too close in time
        #
        secs_passed = (my_io_counters.time -
                       self.io_counters.time)
        if (secs_passed >= 1.0) or (self.last_read_delta is None):
            #
            # more than one second passed since the last measurements
            # (or no last measurements yet exist), calculate new values
            #
            #
            # KB read since the last measurement
            #
            read_delta = (my_io_counters.read -
                          self.io_counters.read) / 1024.0
            #
            # KB written since the last measurement
            #
            write_delta = (my_io_counters.write -
                           self.io_counters.write) / 1024.0
            #
            # save the calculated stats
            #
            self.io_counters = self.io_counters._replace (time=my_io_counters.time,
                                                          read=my_io_counters.read,
                                                          write=my_io_counters.write)
            self.last_read_delta = read_delta
            self.last_write_delta = write_delta
        else:
            #
            # return the same last measurements
            #
            read_delta = self.last_read_delta
            write_delta = self.last_write_delta
        #
        # return time of measurement, read and write activity
        #
        ret_value = DiskActivity._Data (my_io_counters.time,
                                        read_delta,
                                        write_delta)
        return ret_value



class DiskStatsCollector (threading.Thread):
    """
    Collects disk activity statistics with a given frequency.-
    """
    def __init__(self, interval, db):
        """
        Creates a new DiskStatsCollector:

            interval    seconds to sleep between iterations;
            db          SQLite3 database to use.-

        """
        threading.Thread.__init__ (self)
        self._finished = threading.Event ( )
        self.interval = interval
        #
        # create a SA session for the received DB
        #
        engine = create_engine ('sqlite:///%s' % db,
                                echo=False)
        Session = scoped_session (sessionmaker (bind=engine,
                                                autoflush=True))
        DiskActivityEntity.metadata.create_all (engine)
        self.sa_session = Session ( )


    def set_interval (self, interval):
        """
        Set the number of seconds we sleep between task execution.-
        """
        self.interval = interval


    def shutdown (self):
        """
        Stops the collector.-
        """
        self._finished.set ( )


    def run (self):
        """
        Collects usage statistics and saves them in the DB.-
        """
        usage = DiskActivity ( )
        while True:
            if self._finished.isSet ( ):
                return
            else:
                #
                # gather usage data and save it to the DB
                #
                stats = usage.measure ( )
                stats_data = DiskActivityEntity (stats)
                self.sa_session.add (stats_data)
                self.sa_session.commit ( )
            #
            # sleep for 'interval' seconds or until shutdown
            #
            self._finished.wait (self.interval)

