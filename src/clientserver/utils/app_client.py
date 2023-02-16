# A client that simulates the client on our mobile app. For testing purposes only
import queue
import socket
import threading
import struct

from clientserver.tcp import socket_receive


class AppClient:
    """ A client that receives data continuously.
    """
    MSG_LEN = 1024

    def __init__(self, ip: str, port: int, logging: bool = True, save_data: bool = True):
        self.ip = ip
        self.port = port
        self.socket = None

        self._logging = logging
        self._stop = False
        self._save = save_data

        self._rcv_thread = None

        self.data_queue = queue.Queue()

    def connect(self) -> None:
        """ Connect to the server. """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self._log(f"Client connected to {(self.ip, self.port)}")

    def set_timeout(self, timeout: float):
        """ Set a timeout for sending and receiving messages.
        """
        timeval = struct.pack("ll", timeout, 0)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, timeval)

    def _receive(self):
        """ Receive data from the server and put it in a queue.
        """
        while not self._stop:
            try:
                # data = socket_receive(self.socket, self.MSG_LEN)
                # print("Receiving data")
                data = self.socket.recv(1024)
                self._log(data.decode())
                if self._save:
                    self.data_queue.put(data)
                # Send received confirmation message back to server
                # print("Sending confirmation")
                self.socket.sendall("RECVD\r\n".encode("utf-8"))
                # print("Confirmation sent")
            except (ConnectionError, TimeoutError):
                break

    def run(self, daemon: bool = False) -> None:
        """ Start the sending and receiving threads.
        """
        self._rcv_thread = threading.Thread(target=self._receive, daemon=daemon)
        self._rcv_thread.start()

    def join(self):
        self._rcv_thread.join()

    def shutdown(self) -> None:
        """ Stop the threads and close the socket.
        """
        self._log("Stopping client")
        self._stop = True

        self._rcv_thread.join()
        self._log("Client disconnected")

    @staticmethod
    def encode_message(msg: str) -> bytes:
        """ Encode a message to be ready to be sent."""
        msg += "\r\n"
        return msg.encode("utf-8")

    def _log(self, msg: str):
        if self._logging:
            print(msg)
