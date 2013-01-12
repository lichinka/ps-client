import select
import socket
import threading
import time



class WOLSniffer (threading.Thread):
    """
    Wake-On-Lan (WOL) packages sniffer
    """
    def __init__ (self, mac, broadcast='<broadcast>', port=9, amount=10, timeout=30):
        """
        Initialize WOL sniffer.
        """
        threading.Thread.__init__ (self)
        self._finished = threading.Event ( )
        self.bufferSize = 1024
        self.mac_match = mac.upper ()
        self.count = 0;
        self.port = port
        self.broadcast = broadcast
        self.amount = amount
        self.timeout = timeout + 1

    def run (self):
        """
        Start sniffing WOL packages.
        """
        begin = time.time()
        #
        # open socket and listen to broadcasted UDP packages
        #
        self.s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.s.setsockopt (socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.setblocking(0)
        self.s.bind ((self.broadcast, self.port))
        #
        # listen until all packets are received or the stop signal is sent
        #
        while True:
            if self._finished.isSet ( ) or self.count >= self.amount or time.time ( ) - begin > self.timeout:
                break
            r, w, x = select.select ([self.s], [], [])
            for i in r:
                try:
                    data = self.s.recv (1024)
                    if data is not None:
                        self.process_data (data)
                except:
                    pass

    def process_data (self, data):
        """
        Check if received data is WOL package.
        """
        if data is not None and len (data) >= 102:
            dummy = []
            #
            # first six should have value FF (255)
            #
            for i in range (6):
                dummy.append ("%0.2X" % ord (data[i]))
            if ':'.join (dummy) == 'FF:FF:FF:FF:FF:FF':
                forme = True
                #
                # after first six bytes the MAC address should repeat 16 times
                #
                for i in range (16):
                    dummy = []
                    for j in range (6):
                        dummy.append("%0.2X" % ord (data[6+i*6+j]))
                    if ':'.join (dummy) != self.mac_match:
                        forme = False
                        break
                if forme:
                    self.count = self.count + 1

    def shutdown (self):
        """
        Shutdown WOL sniffer.
        """
        self.s.shutdown (socket.SHUT_RDWR)
        self.s.close ( )
        self._finished.set ( )

    def get_count (self):
        """
        Get number of WOL packages received.
        """
        return self.count
