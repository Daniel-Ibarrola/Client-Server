import socket
from collections import deque
import socketserver
import threading


def socket_send(sock: socket.socket, data: bytes, msg_len: int):
    total_sent = 0
    while total_sent < msg_len:
        sent = sock.send(data[total_sent:])
        if sent == 0:
            raise ConnectionError("Socket disconnected")
        total_sent += sent


def socket_receive(sock: socket.socket, msg_len: int):
    chunks = []
    bytes_recv = 0
    while bytes_recv < msg_len:
        chk = sock.recv(min(msg_len - bytes_recv, 2048))
        if chk == b"":
            raise ConnectionError("Socket disconnected")
        chunks.append(chk)
        bytes_recv += len(chk)
    return b"".join(chunks)


class TCPRequestHandler(socketserver.BaseRequestHandler):
    """ Handler for an individual client.
    """

    def handle(self) -> None:
        """ Send all data from the queue to the client.
        """
        for data in TCPServer.buffer:
            try:
                socket_send(self.request, data, TCPServer.MSG_LEN)
                # Client sends a notification that the whole message has been received
                msg = socket_receive(self.request, TCPServer.MSG_LEN)
                if msg.decode(encoding="utf-8") != "RECVD\r\n":
                    break
            except ConnectionError:
                break


class TCPServer:
    """ Server that sends data continuously to multiple clients.
    """
    buffer = None  # type: deque[bytes]
    MSG_LEN = 2048

    def __init__(self, ip: str, port: int, buff_size: int = 100):
        self._ip = ip
        self._port = port

        TCPServer.buffer = deque(maxlen=buff_size)

        self._server = socketserver.ThreadingTCPServer(
            (self._ip, self._port), TCPRequestHandler
        )

    @staticmethod
    def put(data: bytes) -> None:
        """ Put data in the queue. """
        TCPServer.buffer.append(data)

    def run(self):
        """ Starts the thread with the server. """
        server_thread = threading.Thread(
            target=self._server.serve_forever, daemon=True)
        server_thread.start()

    def shutdown(self):
        self._server.shutdown()

    def __enter__(self):
        return self._server.__enter__()

    def __exit__(self, *args):
        return self._server.__exit__(*args)
