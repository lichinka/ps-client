import pytest

from client.linux import PSClientLinux



@pytest.mark.skipif ("sys.platform == 'win32'")
class Test_PSClientLinux ( ):
    """
    This class tests the methods of the PSClient class.-
    """
    def setup (self):
        self.client = PSClientLinux ( )

    def test_check_state (self):
        """
        Checks all supported states are correctly revised.-
        """
        for s in self.client.accepted_states:
            self.client.check_state (s)

