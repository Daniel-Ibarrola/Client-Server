import queue
import socket
import struct
import threading
import time

from clientserver.tcp.socket_ops import socket_receive


class TCPServer:
    """ Server that sends data continuously to multiple clients.
    """
    MSG_LEN = 1024

    def __init__(self, ip: str, port: int, logging: bool = False):
        self._ip = ip
        self._port = port
        self._logging = logging

        self.socket = self._start_socket(self._ip, self._port)
        self._clients = set()  # type: set[socket.socket]
        self._queue = queue.Queue()  # type: queue.Queue[bytes]

        self.STOP = False

        self._accept_thread = None
        self._send_thread = None

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def n_clients(self) -> int:
        return len(self._clients)

    def put(self, data: bytes) -> None:
        """ Put data in the server queue.
        """
        self._queue.put(data)

    def set_timeout(self, timeout: float):
        """ Set the timeout for sending and receiving messages.
        """
        timeval = struct.pack("ll", timeout, 0)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, timeval)

    @staticmethod
    def _start_socket(ip: str, port: int) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, port))
        sock.listen()
        return sock

    def _purge_connections(self, purge: set[socket.socket]) -> None:
        """ Remove disconnected clients. """
        for client in purge:
            self._clients.remove(client)
            self._log("Client disconnected")
        purge.clear()

    def _accept_connection(self) -> None:
        """ Accept new clients. """
        while not self.STOP:
            conn, address = self.socket.accept()
            self._log(f"Connection accepted from {address}")
            self._clients.add(conn)

    def _send_data(self) -> None:
        """ Send new data to all clients. """
        purge = set()

        while not self.STOP:
            if not self._queue.empty() and len(self._clients) > 0:
                data = self._queue.get()
                self._queue.task_done()
                for conn in self._clients:
                    try:
                        conn.sendall(data)
                        rcv_confirmation = conn.recv(1024)
                    except ConnectionError:
                        purge.add(conn)

                self._purge_connections(purge)

            # time.sleep(2)

    def run(self, daemon: bool = True) -> None:
        """ Start the threads to accept new connections and send data to them.
        """
        self._accept_thread = threading.Thread(target=self._accept_connection, daemon=daemon)
        self._send_thread = threading.Thread(target=self._send_data, daemon=daemon)

        self._accept_thread.start()
        self._send_thread.start()

    def serve_forever(self):
        """ Keep the server running forever. """
        self._accept_thread.join()
        self._send_thread.join()

    def shutdown(self) -> None:
        """ Stop the server. """
        self.STOP = True
        self._accept_thread.join()
        self._send_thread.join()

    def _close_connections(self) -> None:
        for conn in self._clients:
            conn.close()

    def _log(self, msg: str) -> None:
        if self._logging:
            print(msg)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """ Closes all sockets. """
        self.socket.close()
        self._close_connections()
