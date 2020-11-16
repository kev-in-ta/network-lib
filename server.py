import socket
import datetime
from cobs import cobs
import bluetooth

class ClWirelessServer:
    """
    Class for connecting to client
    """

    def __init__(self, host, port, protocol = 'TCP'):
        """
        Purpose:    Receives information regarding the port to listen to and creates a socket connection. This class
                    also decodes COBS.
        Passed:     Information to perform connection and protocol to connect to frame module.
        """

        self.protocol = protocol
        self.cobsMessage = ''  # Create variable for storing COBS decoded message

        if self.protocol == 'TCP':
            self.TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.TCPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allows the socket to be reused

            print ("{}: Began connection".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            self.TCPSocket.bind((host, port))
            self.TCPSocket.listen(1)
            self.socket, self.addr = self.TCPSocket.accept()

            print ("{}: Established connection".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        elif self.protocol == 'UDP':

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Initialized.')
            self.socket.bind((host, port))

        elif self.protocol == 'BT':
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.bind((host, port))
            self.sock.listen(1)
            self.socket, self.addr = self.sock.accept()
            print('Initialized.')

    def fnCOBSIntialClear(self):
        """
        Purpose:    Clear out initial code until at the start of a message.
        Passed:     None.
        """

        byte = self.socket.recv(1)

        # Keep looping while byte received is not 0, i.e. the end/start of a cobs message.
        while ord(byte) != 0:

            # Keep looping while not 0
            byte = self.socket.recv(1)
            print("Not 0")

            pass

    def fnShutDown(self):
        """
        Purpose:    Close socket connections on shutdown.
        """

        print("Disconnecting server.")
        self.socket.close()
        print("Disconnected server.")

    def fnRetieveMessage(self):
        """
        Purpose:    Decode received COBS byte string to
        Passed:     None.
        Return:     Status of message.
        """

        if self.protocol == ('TCP' or 'BT'):
            data = []  # List containing characters of byte string
            c = self.socket.recv(1)  # Receive 1 byte of information

            # Continue acquiring bytes of data until end point is reached. Combine into byte string.
            while c != b'\x00':
                if c == b'':
                    self.socket.close()
                    return "Disconnected."
                data.append(c)
                c = self.socket.recv(1)
            data = b''.join(data)

        elif self.protocol == 'UDP':
            data = self.socket.recv(128)

        # Try to decode message and returns exception to avoid closing the program
        try:
            print('Received.')
            return cobs.decode(data)
        except Exception as e:
            print("Failed to decode message due to: {}".format(e))

if __name__ == '__main__':

    host= ''
    port = 64321
    commProtocol = 'TCP'
    #port = 3
    #commProtocol = 'BT'

    print("Server created...")

    instWirelessServer = ClWirelessServer(host, port, protocol=commProtocol)
    instWirelessServer.fnCOBSIntialClear()

    while(True):
        try:
            msg = instWirelessServer.fnRetieveMessage()
            print("{}: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
        except Exception as e:
            print("Message retrieval failed due to: {}".format(e))
            instWirelessServer.fnCOBSIntialClear()

