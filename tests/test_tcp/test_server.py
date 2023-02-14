import socket
import threading
import time
import pytest

from clientserver.tcp.server import TCPServer, socket_receive, socket_send


class FakeClient:

    def __init__(self, ip, port, msg_len):
        self.ip = ip
        self.port = port
        self.msg_len = msg_len

        self.socket = None
        self.stop = False

        self.thread = None

        self.responses = []

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

        self.thread = threading.Thread(target=self.receive, daemon=True)
        self.thread.start()

    def receive(self):
        with self.socket:
            while not self.stop:
                try:
                    data = socket_receive(self.socket, self.msg_len)
                    self.responses.append(data)
                    # Confirm that the message arrived
                    socket_send(self.socket, b"RECVD\r\n", self.msg_len)
                except ConnectionError:
                    self.stop = True

    def shutdown(self):
        self.stop = True
        self.thread.join()


def initialize_server(ip, port):
    start = time.time()

    while time.time() - start < 60:
        try:
            return TCPServer(ip, port, buff_size=5)
        except OSError:
            port += 1

    pytest.fail("Failed to start server")


def get_server_and_clients(port=2000, n_clients=3):
    server = initialize_server("localhost", port)
    TCPServer.MSG_LEN = 7

    clients = [FakeClient(server.ip, server.port, server.MSG_LEN) for _ in range(n_clients)]

    return server, clients


def start_clients(clients):
    for cl in clients:
        cl.start()


def stop_clients(clients):
    for cl in clients:
        cl.shutdown()


def test_server_accepts_and_sends_data_to_multiple_clients():
    server, clients = get_server_and_clients()

    server.put(b"Msg 1\r\n")
    server.put(b"Msg 2\r\n")
    server.put(b"Msg 3\r\n")

    with server:
        server.run()
        start_clients(clients)

        time.sleep(0.1)  # wait for all messages to be received

        server.shutdown()
        stop_clients(clients)

    expected = [b"Msg 1\r\n", b"Msg 2\r\n", b"Msg 3\r\n"]
    assert clients[0].responses == expected
    assert clients[1].responses == expected
    assert clients[2].responses == expected


def test_put_server_buff_size_exceeded():
    server = TCPServer("localhost", 12343, buff_size=2)
    assert len(server.buffer) == 0

    server.put(b"first")
    server.put(b"second")

    assert server.buffer[0].decode() == "first"
    assert server.buffer[1].decode() == "second"

    server.put(b"third")

    assert server.buffer[0].decode() == "second"
    assert server.buffer[1].decode() == "third"


def test_server_sends_when_new_data_arrives():
    server, clients = get_server_and_clients(port=1233, n_clients=2)

    with server:
        server.run()
        start_clients(clients)

        server.put(b"Msg 1\r\n")
        time.sleep(0.2)

        server.put(b"Msg 2\r\n")
        time.sleep(0.2)

        server.shutdown()
        stop_clients(clients)

    expected = [b"Msg 1\r\n", b"Msg 2\r\n"]
    assert clients[0].responses == expected
    assert clients[1].responses == expected


def test_client_disconnects_from_server():
    server, [client] = get_server_and_clients(n_clients=1)
    with server:
        server.run()
        client.start()

        time.sleep(1)
        client.shutdown()
        server.shutdown()

    assert len(client.responses) == 0


def test_server_keeps_track_of_connected_clients():
    server, [client] = get_server_and_clients(n_clients=1)

    server.put(b"Msg 1\r\n")
    server.put(b"Msg 2\r\n")
    with server:
        server.run()
        client.start()
        time.sleep(1)

        # assert server.n_clients == 1

        new_client = FakeClient(server.ip, server.port, server.MSG_LEN)
        new_client.start()
        time.sleep(1)

        # assert server.n_clients == 2

        client.stop = True
        time.sleep(1)

        # assert server.n_clients == 1

        new_client.stop = True
        time.sleep(1)

        # assert server.n_clients == 0
        server.shutdown()

    client.shutdown()
    new_client.shutdown()

    expected = [b"Msg 1\r\n", b"Msg 2\r\n"]
    assert client.responses == expected
    assert new_client.responses == expected
