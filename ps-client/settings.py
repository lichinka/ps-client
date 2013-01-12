###########################################################
##
## Settings file for the PS Client daemon
##
###########################################################
import os.path
import sys
from logging import DEBUG, ERROR
from log.sqlite_handler import SQLiteHandler

#
# base path for this PS Client installation
#
if getattr (sys, 'frozen', False):
    BASE_PATH = os.path.dirname (sys.executable)
else:
    BASE_PATH = os.path.dirname (__file__)


#
# the daemon will listen on this address
# (use 0.0.0.0 to listen on all available addresses)
#
LISTEN_ADDRESS = '0.0.0.0'

#
# whether to start the application in debug mode
#
DEBUG = False

#
# administrators' e-mail addresses
#
ADMINS = ['bostjan.kaluza@gmail.com',
          'dejan5elin@gmail.com',
          'lucas.benedicic@gmail.com']

#
# a secret key used internally for encryption
#
SECRET_KEY = '?\xba,\xa4\x8e\xb3-+\x9a\xa1?\x7b\xcdbdl\xee\x8d$0\x13\x8b12'

#
# local databases
#
LOG_DATABASE = os.path.join (BASE_PATH, 'data/log.db')
STAT_DATABASE = os.path.join (BASE_PATH, 'data/stat.db')

#
# SMTP server through which mails are sent
#
SMTP_SERVER = '127.0.0.1'

#
# Update URL for newer versions of this client
#
UPDATE_URL = 'http://ps.ijs.si/downloads'

#
# a list of the logging handlers that will be
# attached to the Flask application object
#
LOGGING_HANDLERS = []

sql_handler = SQLiteHandler (db=LOG_DATABASE)
sql_handler.setLevel (DEBUG)
LOGGING_HANDLERS.append (sql_handler)

#if not DEBUG:
if False:
    #
    # setup mail logging in case the application is running in production mode
    #
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler (SMTP_SERVER,
                                'client@ps.ijs.si',
                                ADMINS,
                                'PS Client error')
    mail_handler.setLevel (ERROR)
    LOGGING_HANDLERS.append (mail_handler)



def configure (app):
    """
    Configures the application object received.-
    """
    app.config.from_object (__name__)
    for handler in LOGGING_HANDLERS:
        app.logger.addHandler (handler)

