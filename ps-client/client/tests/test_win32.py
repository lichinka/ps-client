import pytest

from client.win32 import PSClientWin



@pytest.mark.skipif ("sys.platform != 'win32'")
class Test_PSClientWin ( ):
    """
    This class tests the methods of the PSClientWin class.-
    """
    def setup (self):
        self.client = PSClientWin ( )

    def test_check_state (self):
        """
        Checks all supported states are correctly revised.-
        """
        for s in self.client.accepted_states:
            self.client.check_state (s)

