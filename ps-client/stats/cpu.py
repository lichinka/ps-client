import time
import psutil
import platform
import threading

from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base ( )
class CpuUsageEntity (Base):
    """
    ORM entity representing this computer's CPU usage.-
    """
    __tablename__ = 'cpu'

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
    # user's CPU utilization (%), including all cores
    #
    user = Column (Float,
                   nullable=False)
    #
    # system CPU utilization (%), including all cores
    #
    system = Column (Float,
                     nullable=False)

    def __repr__ (self):
        return "<CPU (%.3f, %.3f, %.3f)>" % (self.time,
                                             self.user,
                                             self.system)



class CpuUsage (object):
    """
    A class to gather CPU usage statistics.-
    """
    #
    # constants to identify the different types of CPU usage
    #
    _User, _Nice, _System, _Idle = range (4)
    #
    # number of CPU cores in this computer
    #
    NUM_CPUS = psutil.NUM_CPUS

    def _collect (self):
        """
        Collects CPU times per core, using the PSUtil library.-
        """
        my_times = psutil.cpu_times (percpu=False)
        if platform.system ( ) == 'Windows':
            #
            # special time gathering for Windows OS
            #
            ret_value = [my_times.user,
                         0.0,
                         my_times.system,
                         my_times.idle,
                         0.0,
                         0.0,
                         0.0]
        else:
            ret_value = [my_times.user,
                         my_times.nice,
                         my_times.system,
                         my_times.idle,
                         my_times.iowait,
                         my_times.irq,
                         my_times.softirq]
        return ret_value


    def __init__ (self):
        self.cpu_times = self._collect ( )


    def measure (self):
        """
        Returns a tuple containing separated CPU usage percent.
        The result is as follows:

            (time, user_usage, sys_usage)

        where

            time        is the time of the measurement, in seconds since
                        the epoch;
            user_usage  is the percent of the CPU used by user's processes;
            sys_usage   is the percent of the CPU used by process of the
                        system.-

        """
        when = time.time ( )
        my_times = self._collect ( )
        #
        # CPU usage by user's processes
        #
        user_delta = 0.0
        for i in (CpuUsage._User, CpuUsage._Nice):
            user_delta += (my_times[i] - self.cpu_times[i])
        #
        # CPU usage by system processes
        #
        sys_delta = (my_times[CpuUsage._System] -
                     self.cpu_times[CpuUsage._System])
        #
        # total CPU usage
        #
        total_delta = [t0 - t1 for t0, t1 in zip (my_times, self.cpu_times)]
        total_delta = sum (total_delta)
        #
        # the delta may be zero if the measurements are too close in time
        #
        if total_delta > 0.0:
            #
            # save the last CPU usage stats
            #
            self.cpu_times = list (my_times)
            #
            # time of measurement, user's and system usage percent
            #
            ret_value = (when,
                        (user_delta * 100.0) / total_delta,
                        (sys_delta * 100.0) / total_delta)
        else:
            ret_value = (when,
                         total_delta,
                         total_delta)
        return ret_value



class CpuStatsCollector (threading.Thread):
    """
    Collects CPU usage statistics with a given frequency.-
    """
    def __init__(self, interval, db):
        """
        Creates a new CpuStatsCollector:

            interval    seconds to sleep between iterations;
            db          SQLite3 database to use.-

        """
        threading.Thread.__init__ (self,
                                   name='CPU_Usage_Collector_Thread')
        self._finished = threading.Event ( )
        self.interval = interval
        #
        # create a SA session for the received DB
        #
        engine = create_engine ('sqlite:///%s' % db,
                                echo=False)
        Session = scoped_session (sessionmaker (bind=engine,
                                                autoflush=True))
        CpuUsageEntity.metadata.create_all (engine)
        self.sa_session = Session ( )
        self.cpu_usage  = CpuUsage ( )


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
        self.join ( )


    def run (self):
        """
        Collects CPU usage statistics and saves them in the DB.-
        """
        while True:
            if self._finished.isSet ( ):
                return
            else:
                #
                # gather CPU usage data and save it to the DB
                #
                when, usr, sys = self.cpu_usage.measure ( )
                cpu_usage_data = CpuUsageEntity (time=when,
                                                 user=usr,
                                                 system=sys)
                self.sa_session.add (cpu_usage_data)
                self.sa_session.commit ( )
            #
            # sleep for 'interval' seconds or until shutdown
            #
            self._finished.wait (self.interval)

