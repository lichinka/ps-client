import string
import random
import pytest

from client.base import PSClient



class PSClient_Dummy (PSClient):
    """
    Dummy class used for testing the methods of the abstract class.-
    """
    def __init__ (self):
        PSClient.__init__ (self)



class Test_PSClient ( ):
    """
    This class tests the methods of the PSClient abstract class.-
    """
    def setup (self):
        self.client = PSClient_Dummy ( )

    def test_is_accepted_state_raises_exception_on_invalid_parameter (self):
        """
        Checks invalid state parameters raise the ValueError exception.-
        """
        with pytest.raises (ValueError):
            state = ''.join (random.choice (string.letters) for i in xrange (10))
            self.client.is_accepted_state (state)

