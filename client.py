import socket
import datetime
import time
from cobs import cobs
import bluetooth

class ClWirelessClient:
    """
    Class for establishing wireless communications.
    """

    def __init__(self, host, port, protocol='TCP'):
        """
        Purpose:	Initialize various sensors
        Passed: 	Optionally the communication protocol
        """

        # Stores protocol in class variable
        self.protocol = protocol

        # Initiates various socket connections based on passed protocol
        if self.protocol == 'TCP':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(10)

        elif self.protocol == 'UDP':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        elif self.protocol == 'BT':
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.settimeout(10)

        while True:
            try:
                self.socket.connect((host, port))
                break
            except Exception as e:
                print(f'Connection failed: {e}')
                time.sleep(3)
        print('Connected.')

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

    def fnRetieveMessage(self):
        """
        Purpose:    Decode received COBS byte string to
        Passed:     None.
        Return:     Status of message.
        """

        if self.protocol == ('TCP'):
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
            return cobs.decode(data)
        except Exception as e:
            print("Failed to decode message due to: {}".format(e))

    def fnSendMessage(self, message):
        """
        Purpose:
        Passed:
        """

        # Encode message using constant oversized buffering
        dataCobs = cobs.encode(message)

        # Send encoded message through socket
        self.socket.send(dataCobs)

        # Send a 0 value to signal end of message
        if self.protocol == ('TCP' or 'BT'):
            self.socket.send(b'\x00')

    def fnShutDown(self):
        """
        Purpose:	Shutdown sockets
        Passed: 	None
        """

        print('Closing Socket')
        try:
            self.socket.close()
            self.socket.close()
        except Exception as e:
            print(e)

# MAIN PROGRAM

if __name__ == "__main__":

    host = '127.0.0.1'
    port = 64321
    commProtocol = 'TCP'

    print("Creating Client...")

    instWirelessClient = ClWirelessClient(host, port, protocol=commProtocol)

    print("Client created...")

    if (commProtocol != 'UDP'):
        instWirelessClient.fnCOBSIntialClear()

    while (True):
        try:
            msg = instWirelessClient.fnRetieveMessage()
            print("{}: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg.decode('utf-8')))
            if msg == 'Disconnected.':
                instWirelessClient.fnShutDown()
                instWirelessServer = ClWirelessClient(host, port, protocol=commProtocol)
                if (commProtocol != 'UDP'):
                    instWirelessServer.fnCOBSIntialClear()
        except Exception as e:
            print("Message retrieval failed due to: {}".format(e))
            instWirelessClient.fnShutDown()
            instWirelessClient = ClWirelessClient(host, port, protocol=commProtocol)
            if (commProtocol != 'UDP'):
                instWirelessClient.fnCOBSIntialClear()

    """
    # TCP
    # host = '192.168.43.14'
    #host = '10.5.119.18'
    #host = '192.168.43.132'
    #host = '192.168.0.73'
    host = '127.0.0.1'
    port = 64321
    commProtocol = 'TCP'

    # Continuously try to reconnect if connection fails
    while True:

        connectedStatus = False
        instWirelessClient = None

        try:
            print('Connecting to computer...')
            instWirelessClient = ClWirelessClient(host, port, protocol=commProtocol)
            connectedStatus = True
            print('Connected!')

            while True:
                print('Sending!')
                message = b'10.0, 10.0'
                time.sleep(1)
                instWirelessClient.fnSendMessage(message)
                print('Sent!')

        except Exception as e:
            time.sleep(1)
            # Shutdown sockets if necessary
            if connectedStatus:
                instWirelessClient.fnShutDown()
                connectedStatus = False
            print(e)
    """