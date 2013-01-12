import thread
import platform
import netifaces
import time
import json

from datetime import datetime

import cherrypy

import wolsniffer
from client.base import PSClient



class Daemon:
    """
    The PowerServer Client implemented as a CherryPy web application.-
    """
    def __init__ (self, client, esky_wrapper):
        """
        Initialize the daemon application

            `client`        the PSClient object, i.e. the daemon backend;
            `esky_wrapper`  used for packaging the application.-

        """
        if isinstance (client, PSClient):
            self.client = client
        else:
            raise TypeError ('Client object should be a subclass of PSClient')
        #
        # initialize the rest of the attributes
        #
        self.state      = State ( )
        self.wol        = Wol ( )
        self.wrapper    = esky_wrapper
        self.started_at = datetime.now ( )
        #
        # use the same logger as the client object
        #
        self.logger = self.client.logger


    @cherrypy.expose
    def index (self):
        """
        Default response.
        """
        return 'This is PowerServer %s Client - version %s' % (platform.system ( ),
                                                               self.wrapper.version)


    @cherrypy.expose
    def status (self):
        """
        Provide client status: uptime, etc.
        """
        self.logger.info ('Status request received')
        return 'Started at %s' % str (self.started_at)


    @cherrypy.expose
    def update (self):
        """
        Update frozen client.
        """
        self.logger.info ('Update request received')
        message = 'Updating ...'
        if 'NOT FROZEN' not in self.wrapper.version:
            try:
                new_version = self.wrapper.find_update ( )
                if new_version is not None:
                    self.wrapper.auto_update (updater_callback)
                    self.logger.info (message)
                else:
                    message = 'Already the latest version!'
                    self.logger.info (message)

            except Exception:
                message = 'Cannot update the application'
                self.logger.exception (message)
        else:
            message = 'The client cannot be updated as it is not frozen'
            self.logger.error (message)
        return message


    @cherrypy.expose
    def version (self):
        """
        Provide client version.-
        """
        self.logger.info ('Version request received')
        return str (self.wrapper.version)


    @cherrypy.expose
    def restart (self):
        """
        Stop the server. The service/daemon should (re)start it back up.
        """
        self.logger.info ('Restart request received')
        message = 'Restarting...'
        self.logger.info (message)
        cherrypy.engine.exit ( )
        return message


    @cherrypy.expose
    def mac (self, ip=None, callback=None):
        """
        Get MAC address of the adapter corresponding to the IP.
        """
        self.logger.info ('MAC request received')
        #if request.method == 'POST' and request.form.has_key ('ip'):
        #    ip = request.form['ip']
        #else:
        #    ip = request.remote_addr
        if ip is None:
            ip = cherrypy.request.remote.ip
        #callback = request.args.get('callback', None)
        mac = get_mac_int (ip)
        if mac is not None:
            message = '%s has mac %s' % (ip, mac)
            response = jsonify (callback, status='ok', mac=mac, msg=message)
            self.logger.debug (message)
            return response
        else:
            message = 'Cannot find adapter corresponding to given IP %s' % (ip)
            self.logger.error (message)
            response = jsonify (callback, status='error', msg=message)
            return response



class State:
    """
    CherryPy state application
    """
    #@app.route ('/state/apply/<state>')
    @cherrypy.expose
    def apply (self, state):
        """
        Put this computer in the received <state>.-
        """
        #app.logger.info ('Apply-state request received')
        message = ''
        try:
            if this_client.check_state (state):
                #
                # setting state is executed in new thread, in order for the
                # response to be sent before the computer is suspended
                #
                message = "System going into %s state" % state.upper ( )
                thread.start_new_thread (this_client.set_state, (state,))
                #app.logger.info (message)
            else:
                message = 'This system cannot achieve %s mode' % state.upper ( )
                #app.logger.error (message)
        except Exception:
            message = 'Cannot apply %s mode' % state.upper ( )
            #app.logger.exception (message)
        return message



class Wol:
    """
    CherryPy wol application
    """
    #@app.route ('/wol/test', methods=['GET', 'POST'])
    @cherrypy.expose
    def test (self, ip=None, tl=30, count=10, callback=None):
        """
        Capture WOL packages.
        """
        #if request.method == 'POST':
        #    if request.form.has_key('ip'):
        #        ip = request.form['ip']
        #    if request.form.has_key('tl'):
        #        tl = int(request.form['tl'])
        #    if request.form.has_key('count'):
        #        count = int(request.form['count'])
        #    else:
        #        count = 8
        if ip is None:
            ip = cherrypy.request.remote.ip
        tl = int (tl)
        count = int (count)
        #callback = request.args.get ('callback', None)
        mac = get_mac_int (ip)
        if mac is not None:
            sdt = datetime.now()
            sniffer = wolsniffer.WOLSniffer (mac=mac, amount=count, timeout=tl)
            sniffer.start ( )
            while True:
                if not sniffer.is_alive ( ):
                    break
                diff = datetime.now ( ) - sdt
                if diff.total_seconds ( ) >= tl:
                    count = sniffer.get_count ( )
                    sniffer.shutdown ( )
                    break
                time.sleep (0.1)
            message = '%s has received %d magic packets' % (ip, count)
            response = jsonify (callback, status='ok', count=count, msg=message)
            #app.logger.debug (message)
            return response
        else:
            message = 'Can not find adapter corresponding to given IP %s' % (ip)
            response = jsonify (callback, status='error', msg=message)
            #app.logger.error (message)
            return response


#
# Helper methods
#
def updater_callback (result):
    """
    """
    if result['status'] == 'done':
        cherrypy.engine.exit ( )


def get_mac_int (ip):
    """
    """
    for iface in netifaces.interfaces ( ):
        for addr_inet in netifaces.ifaddresses (iface)[netifaces.AF_INET]:
            if addr_inet['addr'] == ip:
                return netifaces.ifaddresses (iface)[netifaces.AF_LINK][0]['addr']
    return None


def jsonify (scallback, *args, **kwargs):
    """
    """
    #s = json.dumps (dict (*args, **kwargs), indent=None if request.is_xhr else 2)
    s = json.dumps (dict (*args, **kwargs), indent=None)
    if scallback is not None:
        s = '%s(%s)' % (scallback, s)
        #mime = 'application/javascript'
    #else:
    #    mime = 'application/json'
    #resp = app.make_response (s)
    #resp.mimetype = mime
    #return resp
    return s



