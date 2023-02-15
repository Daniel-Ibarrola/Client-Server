import time
from collections import deque
import socketserver
import threading
from clientserver.tcp.socket_ops import socket_receive


class TCPRequestHandler(socketserver.BaseRequestHandler):
    """ Handler for an individual client.
    """

    def client_connected(self) -> bool:
        try:
            self.send_and_receive_confirmation(self.request, b"ALIVE\r\n")
        except ConnectionError:
            return False
        return True

    @staticmethod
    def send_and_receive_confirmation(socket, data):
        socket.sendall(data)
        # Client sends a notification that the whole message has been received
        return socket_receive(socket, TCPServer.MSG_LEN)

    def handle(self) -> None:
        """ Send all data from the queue to the client.
        """
        self.handle_new_client()

        # Send the newest data
        prev = TCPServer.latest
        while self.client_connected() and not TCPServer.STOP:
            if TCPServer.latest > prev:
                self.send_and_receive_confirmation(self.request, TCPServer.buffer[-1])
                prev = TCPServer.latest

        TCPServer.n_clients -= 1

    def handle_new_client(self) -> None:
        """ If a new client connects all data in the queue is sent.
        """
        TCPServer.n_clients += 1
        for data in TCPServer.buffer:
            self.send_and_receive_confirmation(self.request, data)


class TCPServer:
    """ Server that sends data continuously to multiple clients.
    """
    buffer = None  # type: deque[bytes]
    MSG_LEN = 2048
    STOP = False
    latest = None

    # NewMessage = threading.Event()
    # WaitAllClients = threading.Barrier()

    n_clients = 0

    def __init__(self, ip: str, port: int, buff_size: int = 100):
        self._setup_server(buff_size)
        self._ip = ip
        self._port = port

        self._server = socketserver.ThreadingTCPServer(
            (self._ip, self._port), TCPRequestHandler
        )

    @property
    def ip(self) -> str:
        return self._ip

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
        cls.n_clients = 0

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
