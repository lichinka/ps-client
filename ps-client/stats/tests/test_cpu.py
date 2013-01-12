import os
import time
import tempfile

from stats.cpu import CpuStatsCollector, CpuUsageEntity



class TestCpuStatsCollector ( ):
    """
    Class for testing CpuStatsCollector functionality.-
    """
    def setup (self):
        #
        # SQLite DB for testing
        #
        self.db_fd, self.db_name = tempfile.mkstemp (suffix='.db')
        #
        # create the collector
        #
        self.collector = CpuStatsCollector (1, self.db_name)


    def test_run (self):
        """
        Checks the collector 'run' method works correctly.-
        """
        self.collector.start ( )
        time.sleep (3)
        self.collector.shutdown ( )

        s = self.collector.sa_session
        last_time = None
        q = s.query (CpuUsageEntity).order_by (CpuUsageEntity.time.desc ( ))
        assert (q.count ( ) > 0)
        for m in q:
            assert (m.user >= 0.0 and m.user < 100.0)
            assert (m.system >= 0.0 and m.system < 100.0)
            if last_time is not None:
                assert (last_time > m.time + self.collector.interval)
            last_time = m.time


    def teardown (self):
        os.close (self.db_fd)
        os.unlink (self.db_name)
