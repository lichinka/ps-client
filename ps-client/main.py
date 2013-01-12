##
##    Usage
##        $> python main.py [configuration file]
##
##    Authors
##        Dejan Petelin, Lucas Benedicic
##
##
import os, sys
import platform
import esky, esky.util

from logging import DEBUG, ERROR

import cherrypy

from daemon import Daemon
from stats.cpu import CpuStatsCollector
from log.sqlite_handler import SQLiteHandler

#
# Platform-dependent import, used by the Esky packager
#
# #if defined('PLATFORM') and PLATFORM == "WIN"
from client.win32 import PSClientWin
# #elif defined('PLATFORM') and PLATFORM == "LINUX"
from client.linux import PSClientLinux
# #endif

#
# TODO enable our SSL adapter
#
#wsgiserver2.ssl_adapters['ps'] = 'ssl.ssl_adapter.psSSLAdapter'



def configure_app (config_file):
    """
    Configures the CherryPy engine with the values given in the 'config_file'.-
    """
    cherrypy.config.update (config_file)
    #
    # start the SQLite-backed logging of the application
    #
    log_db = os.path.join (BASE_PATH,
                           cherrypy.config.get ('log.database'))
    sql_handler = SQLiteHandler (db=log_db)
    sql_handler.setLevel (DEBUG)
    #
    # turn off logging to file ...
    #
    cherrypy.log.error_file = ""
    #
    # ... and activate the SQL-based logging
    #
    cherrypy.log.error_log.addHandler (sql_handler)
    #
    # send Client errors via mail, in case the application is
    # running in production mode
    #
    if cherrypy.config.get ('environment') == 'production':
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler (cherrypy.config.get ('log.smtp_server'),
                                    'client@ps.ijs.si',
                                    cherrypy.config.get ('admins'),
                                    'PS Client error')
        mail_handler.setLevel (ERROR)
        cherrypy.log.error_log.addHandler (mail_handler)
    #
    # configuration successful
    #
    cherrypy.log.error_log.info ("Daemon configured correctly")



#
# Entry point
#
if __name__ == '__main__':
    #
    # base path for this PS Client installation
    #
    if getattr (sys, 'frozen', False):
        BASE_PATH = os.path.dirname (sys.executable)
    else:
        BASE_PATH = os.path.dirname (__file__)

    #
    # read the configuration file
    #
    if len (sys.argv) > 1:
        conf_file = str (sys.argv[1])
    else:
        conf_file = os.path.join (BASE_PATH,
                                  'daemon.config')
    configure_app (conf_file)

    #
    # create the correct PSClient based on the host operating system
    #
    this_client = None
    this_platform = platform.system ( )

    if this_platform == 'Windows':
        this_client = PSClientWin (cherrypy.log.error_log)
        update_url = '%s/win/' % cherrypy.config.get ('update_url')
    elif this_platform == 'Linux':
        this_client = PSClientLinux (cherrypy.log.error_log)
        update_url = '%s/linux/' % cherrypy.config.get ('update_url')
    else:
        #
        # unsupported platform
        #
        cherrypy.log.error_log.error ("%s is not yet supported",
                                      this_platform)
        exit (1)

    #
    # query the application version from the Esky packager
    #
    if hasattr (sys, 'frozen'):
        esky_wrapper = esky.Esky (esky.util.appdir_from_executable (sys.executable),
                                  update_url)
    else:
        esky_wrapper = type ('Enum', ( ), {'version': 'NOT FROZEN'})

    #
    # Esky packager needs this to correctly freeze the application
    #
    cherrypy.engine.autoreload.unsubscribe ( )

    #
    # create the CPU-usage statistics collector
    #
    stats_db = os.path.join (BASE_PATH,
                             cherrypy.config.get ('stats.database'))
    cpu_stat = CpuStatsCollector (int (cherrypy.config.get ('stats.cpu.interval')),
                                  stats_db)
    #
    # start it and register to the event bus to stop it when CherryPy exits
    #
    cpu_stat.start ( )
    cherrypy.engine.subscribe ('stop',
                               cpu_stat.shutdown)
    #
    # start the daemon
    #
    cherrypy.tree.mount   (Daemon (this_client, esky_wrapper),
                           '/')
    cherrypy.engine.start ( )
    cherrypy.engine.block ( )

    #
    # CherryPy server was shut down... the client should decide what to do
    #
    cherrypy.log.error_log.info ("PS-Client has been shut down")
    #this_client.restart ( )

