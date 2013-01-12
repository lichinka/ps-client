from abc import ABCMeta



class PSClient (object):
    """
    An abstract class representing a PowerServer client computer.-
    """
    __metaclass__ = ABCMeta

    #
    # the states this computer may change into
    #
    accepted_states = ('suspend',
                       'hibernate',
                       'shutdown')

    def __init__ (self, logger=None):
        """
        Creates a new instance of a PSClient.

            `logger`    is an object following the standard Python Logger
                        interface.-

        """
        #
        # we will use a default console-based logger if none was given
        #
        if logger is None:
            import logging
            ch = logging.StreamHandler ( )
            ch.setLevel (logging.INFO)
            self.logger = logging.getLogger ('PS-Client')
            self.logger.addHandler (ch)
        else:
            self.logger = logger


    def is_accepted_state (self, state):
        """
        Returns True if the received 'state' is recognized by this class;
        otherwise it raises 'ValueError' exception.-
        """
        if state in self.accepted_states:
            return True
        else:
            raise ValueError ("Unknown state. Try one of %s" % str (self.accepted_states))

    def check_state (self, state):
        """
        Returns True if the current user has permission to change this
        computer's received 'state', and the system supports it.

            state:  Any value of self.accepted_states.-

        """
        raise NotImplementedError ( )

    def set_state (self, state):
        """
        Changes this computer's current state.

            state:  Any value of self.accepted_states.-

        """
        raise NotImplementedError ( )

    def appexe_from_executable (self, exepath):
        appdir = appdir_from_executable (exepath)
        exename = os.path.basename (exepath)
        return os.path.join (appdir,exename)

    def restart (self):
        """
            Restart the application after update
        """
        raise NotImplementedError ( )

