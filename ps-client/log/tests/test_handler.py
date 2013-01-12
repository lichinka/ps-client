import os
import random
import pytest
import logging
import sqlite3
import tempfile

from log.sqlite_handler import SQLiteHandler



class Test_SQLiteHandler ( ):
    """
    Checks correct functioning of the SQLite-based logger.-
    """
    def setup_class (cls):
        #
        # SQLite DB for testing
        #
        cls.db_fd, cls.db_name = tempfile.mkstemp (suffix='.db')
        #
        # setup logging for testing
        #
        cls.sql_handler = SQLiteHandler (db=cls.db_name)
        cls.logger = logging.getLogger (cls.__name__)
        cls.logger.setLevel (logging.DEBUG)
        cls.logger.addHandler (cls.sql_handler)

    def teardown_class (cls):
        os.close (cls.db_fd)
        os.unlink (cls.db_name)



class Test_debug (Test_SQLiteHandler):
    """
    Tests logging debug messages.-
    """
    def test (self):
        #
        # log some debug messages
        #
        expected_count = random.randint (1, 20)
        for i in range (expected_count):
            self.logger.debug ('i = %d' % i)
        #
        # connect to the database and check they are correct
        #
        con = sqlite3.connect (self.db_name)
        with con:
            #
            # received rows are dictionaries instead of tuples
            #
            con.row_factory = sqlite3.Row

            cur = con.cursor ( )
            cur.execute ('SELECT COUNT(*) FROM log;')
            actual_count = cur.fetchone ( )
            actual_count = int (actual_count[0])
            assert (actual_count == expected_count)

            cur.execute ('SELECT * FROM log ORDER BY created ASC;')
            i = 0
            for row in cur.fetchall ( ):
                expected = 'DEBUG'
                assert (row['LogLevelName'] == expected)
                expected = 'i = %d' % i
                assert (row['Message'] == expected)
                i += 1



class Test_exception (Test_SQLiteHandler):
    """
    Tests logging of exceptions.-
    """
    @pytest.mark.xfail
    def test_this_one_should_fail_with_ZeroDivisionError (self):
        #
        # raise a ZeroDivisionError on purpose
        #
        return int (3 / 0)


    def test_exception_has_been_logged (self):
        #
        # connect to the database and check the exception is there
        #
        con = sqlite3.connect (self.db_name)
        with con:
            #
            # received rows are dictionaries instead of tuples
            #
            con.row_factory = sqlite3.Row

            cur = con.cursor ( )
            cur.execute ('SELECT COUNT(*) FROM log;')
            actual_count = cur.fetchone ( )
            actual_count = int (actual_count[0])
            cur.execute ('SELECT * FROM log;')
            for row in cur.fetchall ( ):
                expected = 'ERROR'
                assert (row['LogLevelName'] == expected)
                expected = str (ZeroDivisionError)
                assert (row['Message'] == expected)
