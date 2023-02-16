import queue
import time
import threading
import socket
import pytest

from clientserver.utils.app_client import AppClient
from clientserver.tcp import socket_receive


SERVER_QUEUE = queue.Queue()


def initialize_server(ip, port):
    start = time.time()

    while time.time() - start < 60:
        try:
            return create_server(ip, port), port
        except OSError:
            port += 1

    pytest.fail("Failed to start server")


def create_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen()

    return sock


def server_send(server):
    connection, _ = server.accept()

    with connection as conn:
        for ii in range(3):
            message = f"msg {ii + 1}\r\n".encode("utf-8")
            conn.sendall(message)

            response = socket_receive(conn, 7)
            SERVER_QUEUE.put(response)


def test_app_client():
    ip, port = "localhost", 12345

    server, port = initialize_server(ip, port)
    server_thread = threading.Thread(target=server_send, args=(server,), daemon=True)
    server_thread.start()

    client = AppClient(ip, port, logging=False)
    client.MSG_LEN = 7
    client.connect()
    client.run(daemon=True)

    server_thread.join()
    client.shutdown()

    assert client.data_queue.get() == b"msg 1\r\n"
    assert client.data_queue.get() == b"msg 2\r\n"
    assert client.data_queue.get() == b"msg 3\r\n"
    assert client.data_queue.empty()

    assert not SERVER_QUEUE.empty()
    assert SERVER_QUEUE.get() == b"RECVD\r\n"
    assert SERVER_QUEUE.get() == b"RECVD\r\n"
    assert SERVER_QUEUE.get() == b"RECVD\r\n"

    assert SERVER_QUEUE.empty()
