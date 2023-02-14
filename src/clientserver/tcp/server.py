import time
from collections import deque
import socketserver
import threading
from clientserver.tcp import socket_send, socket_receive


class TCPRequestHandler(socketserver.BaseRequestHandler):
    """ Handler for an individual client.
    """

    @staticmethod
    def send_and_receive_confirmation(socket, data):
        socket_send(socket, data, TCPServer.MSG_LEN)
        # Client sends a notification that the whole message has been received
        return socket_receive(socket, TCPServer.MSG_LEN)

    def handle(self) -> None:
        """ Send all data from the queue to the client.
        """
        self.handle_new_client()

        # Send the newest data
        prev = TCPServer.latest
        while not TCPServer.STOP:
            if TCPServer.latest > prev:
                try:
                    self.send_and_receive_confirmation(self.request, TCPServer.buffer[-1])
                except ConnectionError:
                    break
                prev = TCPServer.latest

    def handle_new_client(self) -> None:
        """ If a new client connects all data in the queue is sent.
        """
        for data in TCPServer.buffer:
            try:
                msg = self.send_and_receive_confirmation(self.request, data)
                if msg.decode(encoding="utf-8") != "RECVD\r\n":
                    break
            except ConnectionError:
                break


class TCPServer:
    """ Server that sends data continuously to multiple clients.
    """
    buffer = None  # type: deque[bytes]
    MSG_LEN = 2048
    STOP = False
    latest = None

    def __init__(self, ip: str, port: int, buff_size: int = 100):
        self._setup_server(buff_size)
        self._ip = ip
        self._port = port

        self._server = socketserver.ThreadingTCPServer(
            (self._ip, self._port), TCPRequestHandler
        )
        self._server.allow_reuse_address = True

    @property
    def port(self) -> int:
        return self._port

    @classmethod
    def put(cls, data: bytes) -> None:
        """ Put data in the buffer. """
        cls.latest = time.time()
        cls.buffer.append(data)

    @classmethod
    def _setup_server(cls, buff_size):
        cls.buffer = deque(maxlen=buff_size)
        cls.STOP = False
        cls.latest = time.time()

    def run(self):
        """ Starts the thread with the server. """
        server_thread = threading.Thread(
            target=self._server.serve_forever, daemon=True)
        server_thread.start()

    def shutdown(self):
        TCPServer.STOP = True
        self._server.shutdown()

    def __enter__(self):
        return self._server.__enter__()

    def __exit__(self, *args):
        return self._server.__exit__(*args)
