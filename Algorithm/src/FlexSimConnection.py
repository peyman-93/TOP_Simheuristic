import subprocess
import socket

class FlexSimConnection():
    """
    Class for connecting and communicating with FlexSim
    """

    def __init__(self, flexsimPath, modelPath, address='localhost', port=5005, verbose=False, visible=True):
        self.flexsimPath = flexsimPath
        self.modelPath = modelPath
        self.address = address
        self.port = port
        self.verbose = verbose
        self.visible = visible

        # self._launch_flexsim()

    def _launch_flexsim(self):
        """
        launch FlexSim
        """
        if self.verbose:
            print("Launching " + self.flexsimPath + " " + self.modelPath)

        args = [self.flexsimPath, self.modelPath]
        if self.visible == False:
            args.append("-maintenance")
            args.append("nogui")
        self.flexsimProcess = subprocess.Popen(args)

        self._socket_init(self.address, self.port)

    def _close_flexsim(self):
        """
        close FlexSim
        """
        self.flexsimProcess.kill()
        self._socket_end(self.address, self.port)
        if self.verbose:
            print("FlexSim closed. Ready to re-connect.")

    def _socket_init(self, host, port):
        """
        Initiate socket connection
        """
        if self.verbose:
            print("Waiting for FlexSim to connect to socket on " +
                  self.address + ":" + str(self.port))

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.listen()

        (self.clientsocket, self.socketaddress) = self.serversocket.accept()
        if self.verbose:
            print("Socket connected")

        if self.verbose:
            print("Waiting for READY message")
        message = self._socket_recv()
        # if self.verbose:
        #     print(message.decode('utf-8'))
        if message != b"READY":
            raise RuntimeError("Did not receive READY! message")

    def _socket_end(self, host, port):
        """
        End socket connection
        """
        if self.verbose:
            print("Closing socket")
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.close()

    def _socket_send(self, msg):
        """
        Send message through socket
        """
        totalsent = 0
        while totalsent < len(msg):
            sent = self.clientsocket.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent = totalsent + sent
        if self.verbose:
            print(">Sent: {}".format(msg.decode('utf-8')))

    def _socket_recv(self):
        """
        Receive message from socket
        """
        chunks = []
        while 1:
            chunk = self.clientsocket.recv(2048)
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            if chunk[-1] == ord('!'):
                chunks.append(chunk[:-1])
                break
            else:
                chunks.append(chunk)
        if self.verbose:
            print("<Recv: {}".format(chunks[0].decode('utf-8')))
        return b''.join(chunks)

# Functions
def main():
    pass

# Main execution:
if __name__ == "__main__":
    main()