# A client that simulates the client on our mobile app. For testing purposes only
import queue
import threading

from clientserver.tcp.client import AbstractClient


class AppClient(AbstractClient):
    """ A client that receives data continuously.
    """
    MSG_LEN = 1024

    def __init__(self, ip: str, port: int, logging: bool = True, save_data: bool = True):
        super().__init__(ip, port, logging)

        self._save = save_data
        self._rcv_thread = None
        self.data_queue = queue.Queue()

    def _receive(self):
        """ Receive data from the server and put it in a queue.
        """
        while not self._stop:
            try:
                # data = socket_receive(self.socket, self.MSG_LEN)
                data = self._socket.recv(1024)
                self._log(data.decode())
                if self._save:
                    self.data_queue.put(data)
                # Send received confirmation message back to server
                self._socket.sendall("RECVD\r\n".encode("utf-8"))
            except (ConnectionError, TimeoutError):
                break

    def run(self, daemon: bool = False) -> None:
        """ Start the receiving thread.
        """
        self._rcv_thread = threading.Thread(target=self._receive, daemon=daemon)
        self._rcv_thread.start()

    def join(self):
        self._rcv_thread.join()

    def shutdown(self) -> None:
        """ Stop the threads and close the socket.
        """
        self._stop = True
        self._log("Stopping client")

        self._rcv_thread.join()
        self._log("Client disconnected")
