import sqlite3
import logging



class SQLiteHandler (logging.Handler):
    """
    Logging handler for SQLite.

    This version sacrifices performance for thread-safety, as it opens/closes
    connections for each log entry. This is necessary in multi-threaded
    applications, because SQLite doesn't allow access to objects across
    different threads.

    Based on Vinay Sajip's DBHandler class:

        http://www.red-dove.com/python_logging.html

    """
    Create_sql = """CREATE TABLE IF NOT EXISTS log (Created float,
                                                    Name text,
                                                    LogLevel int,
                                                    LogLevelName text,
                                                    Message text,
                                                    Args text,
                                                    Module text,
                                                    FuncName text,
                                                    LineNo int,
                                                    Exception text,
                                                    Process int,
                                                    Thread text,
                                                    ThreadName text
                                                    )"""
    Insert_sql = """INSERT INTO log (Created,
                                     Name,
                                     LogLevel,
                                     LogLevelName,
                                     Message,
                                     Args,
                                     Module,
                                     FuncName,
                                     LineNo,
                                     Exception,
                                     Process,
                                     Thread,
                                     ThreadName)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

    def __init__ (self, db='log.db'):
        logging.Handler.__init__ (self)
        self.db = db
        #
        # create the log table if needed
        #
        conn = sqlite3.connect (self.db)
        conn.execute (SQLiteHandler.Create_sql)
        conn.commit ( )

    def emit (self, record):
        #
        # in case we are logging an exception, format its text
        #
        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException (record.exc_info)
        else:
            record.exc_text = ""
        #
        # insert the log record
        #
        conn = sqlite3.connect (self.db)
        conn.execute (SQLiteHandler.Insert_sql, (float (record.__dict__['created']),
                                                 str (record.__dict__['name']),
                                                 int (record.__dict__['levelno']),
                                                 str (record.__dict__['levelname']),
                                                 str (record.__dict__['msg']),
                                                 str (record.__dict__['args']),
                                                 str (record.__dict__['module']),
                                                 str (record.__dict__['funcName']),
                                                 int (record.__dict__['lineno']),
                                                 str (record.__dict__['exc_text']),
                                                 int (record.__dict__['process']),
                                                 str (record.__dict__['thread']),
                                                 str (record.__dict__['threadName'])))
        conn.commit ( )
