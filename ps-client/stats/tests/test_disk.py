import os
import time
import random
import tempfile

from stats.disk import DiskStatsCollector, DiskActivityEntity



class TestDiskStatsCollector ( ):
    """
    Class for testing DiskStatsCollector functionality.-
    """
    def setup (self):
        #
        # SQLite DB for testing
        #
        self.db_fd, self.db_name = tempfile.mkstemp (suffix='.db')
        #
        # create the collector
        #
        self.collector = DiskStatsCollector (1, self.db_name)


    def test_scattered_measurements_are_different (self):
        """
        Measurements taken within MORE than a second should be different.-
        """
        #
        # start the disk statistics collector
        #
        collecting_time = time.time ( )
        self.collector.set_interval (1.1)
        self.collector.start ( )
        #
        # generate some random disk activity
        #
        for i in xrange (100):
            tmp_fd, tmp_name = tempfile.mkstemp (suffix='.tmp')
            # write activity
            f = open (tmp_name, 'w')
            for j in xrange (10000):
                f.write (str (random.random ( )))
                f.write ('\n')
            f.flush ( )
            f.close ( )
            # read activity
            f = open (tmp_name, 'r')
            for line in f:
                pass
            f.close ( )
            os.close (tmp_fd)
            os.unlink (tmp_name)
            time.sleep (0.1)
        #
        # stop the collector
        #
        self.collector.shutdown ( )
        collecting_time = time.time ( ) - collecting_time
        #
        # check the correctness of the gathered statistics
        #
        s = self.collector.sa_session
        last_m = None
        q = s.query (DiskActivityEntity).order_by (DiskActivityEntity.time.desc ( ))
        assert (q.count ( ) > 0)
        assert (q.count ( ) < (collecting_time / self.collector.interval) + 1)
        reads = []
        writes = []
        for m in q:
            reads.append (float (m.read))
            writes.append (float (m.write))
            if last_m is not None:
                assert (last_m.time > m.time + self.collector.interval)
            last_m = m
        assert (min (writes) != max (writes))


    def test_crowded_measurements_are_equal (self):
        """
        Measurements taken within LESS than a second should be identical.-
        """
        collecting_time = 0.9
        self.collector.set_interval (0.1)
        self.collector.start ( )
        time.sleep (collecting_time)
        self.collector.shutdown ( )

        s = self.collector.sa_session
        last_m = None
        q = s.query (DiskActivityEntity).order_by (DiskActivityEntity.time.desc ( ))
        assert (q.count ( ) > 0)
        assert (q.count ( ) < (collecting_time / self.collector.interval) + 1)
        for m in q:
            assert (m.read >= 0.0)
            assert (m.write >= 0.0)
            if last_m is not None:
                assert (last_m.read == m.read)
                assert (last_m.write == m.write)
                assert (last_m.time > m.time + self.collector.interval)
            last_m = m


    def teardown (self):
        os.close (self.db_fd)
        os.unlink (self.db_name)

