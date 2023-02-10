
import socket
import threading
from typing import Any, Optional


class EchoServer:
    """A server that receives data from a single client and sends it back.
    """

    def __init__(self, ip: str, port: int,
                 save_data: Optional[bool] = False,
                 logging: Optional[bool] = True
                 ):
        self.ip = ip
        self.port = port
        self.socket = None

        self._save_data = save_data
        self._logging = logging

        self._run_thread = None
        self.STOP = False

        self._data = []

    @property
    def data(self) -> list[Any]:
        return self._data

    def _accept_connection(self) -> socket.socket:
        """ Start the server.
        """
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

        connection, address = self.socket.accept()
        self._log(f"Server accepted connection from {address}")
        return connection

    def _main_loop(self) -> None:
        """ Main loop receives a message from the client and sends it back.
        """
        connection = self._accept_connection()

        with connection:
            while not self.STOP:
                try:
                    data = connection.recv(4096)
                    connection.sendall(data)

                    if len(data) > 0:
                        data = data.decode().rstrip()
                        if self._save_data:
                            self._data.append(data)
                        self._log(f"Client: {data}")

                except ConnectionError:
                    self._log(f"Client disconnected.")
                    break

    def run(self, forever: Optional[bool] = False) -> None:
        """ Listen for connections and start main loop. """
        self._log("Starting echo server")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._run_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._run_thread.start()

        if forever:
            self._run_thread.join()

    def shutdown(self) -> None:
        self.STOP = True
        self._log("Shutting down server...")

        self._run_thread.join()
        self.socket.close()
        self._log("Stopped server")

    def _log(self, msg: str) -> None:
        """ Print messages to console. """
        if self._logging:
            print(msg)
