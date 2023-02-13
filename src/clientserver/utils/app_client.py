# A client that simulates the client on our mobile app. For testing purposes only
import queue
import socket
import time
import threading


class AppClient:
    """ A client that receives data continuously.
    """

    def __init__(self, ip: str, port: int, logging: bool = True):
        self.ip = ip
        self.port = port
        self.socket = None

        self._logging = logging
        self._stop = False

        self._rcv_thread = None
        self._send_thread = None

        self.data_queue = queue.Queue()

    def connect(self) -> None:
        """ Connect to the server. """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self._log(f"Client connected to {(self.ip, self.port)}")

    def _receive(self):
        """ Receive data from the server and put it in a queue.
        """
        while not self._stop:
            try:
                data = self.socket.recv(4096)
            except ConnectionError:
                break

            if len(data) > 0:
                self.data_queue.put(data)
                self._log(data.decode())

    def _send(self, wait: float):
        """ Send a message every certain time to the server.
        """
        message = self.encode_message("Hola")
        while not self._stop:
            try:
                self.socket.send(message)
            except ConnectionError:
                break
            time.sleep(wait)

    def run(self, wait: float, forever: bool = False) -> None:
        """ Start the sending and receiving threads.
        """
        self._rcv_thread = threading.Thread(target=self._receive, daemon=True)
        self._send_thread = threading.Thread(target=self._send, args=(wait,), daemon=True)
        self._rcv_thread.start()
        self._send_thread.start()

        if forever:
            self._send_thread.join()
            self._rcv_thread.join()

    def shutdown(self) -> None:
        """ Stop the threads and close the socket.
        """
        self._log("Stopping client")
        self._stop = True

        self._rcv_thread.join()
        self._send_thread.join()

        self.socket.close()
        self._log("Client disconnected")

    @staticmethod
    def encode_message(msg: str) -> bytes:
        """ Encode a message to be ready to be sent."""
        msg += "\r\n"
        return msg.encode("utf-8")

    def _log(self, msg):
        if self._logging:
            print(msg)
