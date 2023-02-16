import socket
import threading
import time
import pytest

from clientserver.tcp.server import TCPServer, socket_receive


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
                    if data != b"ALIVE\r\n":
                        self.responses.append(data)
                    # Confirm that the message arrived
                    self.socket.sendall(b"RECVD\r\n")
                except ConnectionError:
                    self.stop = True

    def shutdown(self):
        self.stop = True
        self.thread.join()


def initialize_server(ip, port):
    start = time.time()

    while time.time() - start < 60:
        try:
            return TCPServer(ip, port)
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


def test_server_sends_new_data_when_it_arrives():
    server, clients = get_server_and_clients(port=1233, n_clients=2)

    with server:
        server.run()
        start_clients(clients)

        server.put(b"Msg 1\r\n")
        time.sleep(0.5)

        server.put(b"Msg 2\r\n")
        time.sleep(0.5)

        server.shutdown()
        stop_clients(clients)

    expected = [b"Msg 1\r\n", b"Msg 2\r\n"]
    assert clients[0].responses == expected
    assert clients[1].responses == expected


def test_all_new_data_is_sent():
    server, clients = get_server_and_clients(port=1233, n_clients=1)

    with server:
        server.run()
        start_clients(clients)

        # All data arrives simultaneously
        server.put(b"Msg 1\r\n")
        server.put(b"Msg 2\r\n")
        server.put(b"Msg 3\r\n")

        server.shutdown()
        stop_clients(clients)

    expected = [b"Msg 1\r\n", b"Msg 2\r\n", b"Msg 3 \r\n"]
    assert clients[0].responses == expected


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

    with server:
        server.run()
        client.start()
        time.sleep(1)

        assert server.n_clients == 1

        new_client = FakeClient(server.ip, server.port, server.MSG_LEN)
        new_client.start()
        time.sleep(0.5)

        assert server.n_clients == 2

        client.stop = True
        time.sleep(0.5)

        assert server.n_clients == 1

        new_client.stop = True
        time.sleep(0.5)

        server.shutdown()

    client.shutdown()
    new_client.shutdown()

    assert server.n_clients == 0
