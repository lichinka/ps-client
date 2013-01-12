import os
import sys

from client.base import PSClient



class PSClientLinux (PSClient):
    """
    This class represents a PowerServer client computer,
    running the Linux OS.-
    """
    def _create_dbus_object (self, clazz, path):
        """
        Returns a tuple containing a DBus object, accessible
        through the system interface, and its properties.

            class:  the class of the object to be created;
            path:   the path to the object to be created.-

        """
        try:
            import dbus
        except ImportError:
            raise ImportError ("DBus for Python is not installed. Install the 'dbus-python' package.")
        #
        # create a DBus object
        #
        system_bus = dbus.SystemBus ( )
        try:
            obj = system_bus.get_object (clazz, path)
            obj_prop = dbus.Interface (obj,
                                       'org.freedesktop.DBus.Properties')
            return (obj, obj_prop)
        except dbus.exceptions.DBusException, e:
            self.logger.error ('Cannot activate object %s\n' % clazz)
            self.logger.error ("\t%s\nIs the provider installed?" % str (e))
            raise dbus.exceptions.DBusException


    def __init__ (self, logger=None):
        """
        Creates a new instance of a PS-Client for Linux.

            `logger`    is an object following the standard Python Logger
                        interface.-

        """
        PSClient.__init__ (self, logger)
        #
        # UPower control object path and class for DBus
        #
        self.upower_path = '/org/freedesktop/UPower'
        self.upower_class = 'org.freedesktop.UPower'
        #
        # ConsoleKit control object path and class for DBus
        #
        self.ck_path = '/org/freedesktop/ConsoleKit/Manager'
        self.ck_class = 'org.freedesktop.ConsoleKit'
        #
        # inform about the client's object creation
        #
        self.logger.info ("PS-Client for Linux created")


    def check_state (self, state):
        """
        Returns True if the current user has permission to change this
        computer's received 'state', and the system supports it.

            state:  Any value of self.accepted_states.-

        """
        #
        # check the received state is valid
        #
        self.is_accepted_state (state)
        #
        # create an UPower object with its properties
        #
        upower, upower_prop = self._create_dbus_object (self.upower_class,
                                                        self.upower_path)
        if state == 'suspend':
            #
            # is this system able to suspend?
            #
            ret_value = bool (upower_prop.Get (self.upower_class, 'CanSuspend'))
            #
            # does the user have permission to suspend?
            #
            ret_value &= bool (upower.SuspendAllowed (dbus_interface=self.upower_class))
        elif state == 'hibernate':
            #
            # is this system able to hibernate?
            #
            ret_value = bool (upower_prop.Get (self.upower_class, 'CanHibernate'))
            #
            # does the user have permission to hibernate?
            #
            ret_value &= bool (upower.HibernateAllowed (dbus_interface=self.upower_class))
        elif state == 'shutdown':
            consolekit = self._create_dbus_object (self.ck_class,
                                                   self.ck_path)
            consolekit = consolekit[0]
            #
            # is this system/user able to shutdown?
            #
            ret_value = bool (consolekit.CanStop (dbus_interface=self.ck_class + '.Manager'))
        else:
            ret_value = False
        return ret_value


    def set_state (self, state):
        """
        Changes this computer's current state.

            state:  Any value of self.accepted_states.-

        """
        #
        # is this state achivable on this computer?
        #
        if self.check_state (state):
            upower = self._create_dbus_object (self.upower_class,
                                               self.upower_path)
            upower = upower[0]
            #
            # send the correct state command, based on the received parameter
            #
            if state == 'suspend':
                upower.Suspend (dbus_interface=self.upower_class)
            elif state == 'hibernate':
                upower.Hibernate (dbus_interface=self.upower_class)
            elif state == 'shutdown':
                consolekit = self._create_dbus_object (self.ck_class,
                                                       self.ck_path)
                consolekit = consolekit[0]
                consolekit.Stop (dbus_interface=self.ck_class + '.Manager')
        else:
            raise SystemError ("System cannot achieve state '%s'" % state)


    def restart (self):
        appexe = self.appexe_from_executable (sys.executable)
        if os.path.splitext (os.path.basename (appexe))[0] == 'python':
            os.execv (appexe, [appexe] + sys.argv[0:])
        else:
            os.execv (appexe, [appexe] + sys.argv[1:])

