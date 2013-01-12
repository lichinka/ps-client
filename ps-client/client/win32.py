import sys
import ctypes
import platform
if platform.system ( ) == 'Windows':
    import winerror
    import win32api
    import win32security

from client.base import PSClient



class PSClientWin (PSClient):
    """
    This class represents a PowerServer client computer,
    running a Windows XP OS or newer.-
    """
    def __init__ (self, logger=None):
        """
        Creates a new instance of a PS-Client for Windows.

            `logger`    is an object following the standard Python Logger
                        interface.-

        """
        PSClient.__init__ (self, logger)
        #
        # inform about the client's object creation
        #
        self.logger.info ("PS-Client for Windows created")


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
        # try to enable the required privileges to change the power state
        #
        privilege_flags = win32security.TOKEN_ADJUST_PRIVILEGES | \
                          win32security.TOKEN_QUERY
        token_handle = win32security.OpenProcessToken (win32api.GetCurrentProcess ( ),
                                                       privilege_flags)
        privilege_id = win32security.LookupPrivilegeValue (None,
                                                           win32security.SE_SHUTDOWN_NAME)
        #
        # does the user have permission to change the power state?
        #
        win32security.AdjustTokenPrivileges (token_handle,
                                             0,
                                             [(privilege_id,
                                               win32security.SE_PRIVILEGE_ENABLED)])
        ret_value = win32api.GetLastError ( )
        ret_value = (ret_value == winerror.ERROR_SUCCESS)
        return ret_value


    def set_state (self, state):
        """
        Changes this computer's current state.

            state:  Any value of self.accepted_states.-

        """
        #
        # is this state achievable on this computer?
        #
        if self.check_state (state):
            #
            # send the correct state command, based on the received parameter
            #
            if state == 'suspend':
                ctypes.windll.powrprof.SetSuspendState (0, 0, 0)
            elif state == 'hibernate':
                ctypes.windll.powrprof.SetSuspendState (1, 0, 0)
            elif state == 'shutdown':
                ctypes.windll.advapi32.InitiateSystemShutdown (None,
                                                               'Shutdown initiated by PowerServer',
                                                               90,
                                                               0,
                                                               0)
        else:
            raise SystemError ("System cannot achieve state '%s'" % state)

    def restart (self):
        # TODO: find out if the client is running as windows service or as regular executable/script
        # if windows service, restart it
        # the easiest way to restart the windows service is raising an exception... the system will automatically restart the service
        sys.exit ('updated')
        # otherwise restart the application


