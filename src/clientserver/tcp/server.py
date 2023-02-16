import queue
import socketserver
import threading
import time

from clientserver.tcp.socket_ops import socket_receive


class SnapshotQueue(queue.Queue):
    def snapshot(self):
        with self.mutex:
            return list(self.queue)


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
        """ Send incoming data to the client.
        """
        TCPServer.n_clients += 1

        prev = TCPServer.latest
        while self.client_connected() and not TCPServer.STOP:
            if TCPServer.latest > prev:
                self.send_and_receive_confirmation(self.request, TCPServer.buffer.snapshot()[-1])
                prev = TCPServer.latest

        TCPServer.n_clients -= 1


class TCPServer:
    """ Server that sends data continuously to multiple clients.
    """
    buffer = None  # type: SnapshotQueue
    MSG_LEN = 2048
    STOP = False
    latest = None

    # NewMessage = threading.Event()
    # WaitAllClients = threading.Barrier()

    n_clients = 0

    def __init__(self, ip: str, port: int):
        self._setup_server()
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
        cls.buffer.put(data)

    @classmethod
    def _setup_server(cls):
        cls.buffer = SnapshotQueue()
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
