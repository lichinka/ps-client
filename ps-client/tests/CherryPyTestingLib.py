import imp
import os, os.path

import cherrypy

class CherryPyTestingLib (object):
    def setup_cherrypy (self, conf_file=None):
        """
        Configures the CherryPy engine and server using
        the built-in 'embedded' environment mode.

        If provided, `conf_file` is a path to a CherryPy
        configuration file used in addition.
        """
        cherrypy.config.update ({"environment": "embedded"})
        if conf_file:
            cherrypy.config.update (conf_file)

    def start_cherrypy (self):
        """
        Starts a CherryPy engine.
        """
        cherrypy.engine.start ( )

    def exit_cherrypy (self):
        """
        Terminates a CherryPy engine.
        """
        cherrypy.engine.exit ( )

    def mount_application (self, appmod, appcls, directory=None):
        """
        Mounts an application to be tested. `appmod` is the name
        of a Python module containing `appcls`. The module is
        looked for in the given directory. If not provided, we use
        the current one instead.
        """
        directory = directory or os.getcwd()
        fileobj, filename, description = imp.find_module(appmod, [directory])
        mod = imp.load_module(appmod, fileobj, filename, description)
        if hasattr(mod, appcls):
            cls = getattr (mod, appcls)
            app = cls ( )
            cherrypy.tree.mount (app)
        else:
            raise ImportError, "cannot import name %s from %s" % (appcls, appmod)

