import time
import pytest

from clientserver.tcp.server import TCPServer
from clientserver.utils.app_client import AppClient


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
    clients = [
        AppClient(server.ip, server.port, logging=False, save_data=True)
        for _ in range(n_clients)
    ]
    server.set_timeout(3)

    return server, clients


def start_clients(clients: list[AppClient]):
    for cl in clients:
        cl.connect()
        cl.set_timeout(2)
        cl.run(daemon=True)


def stop_clients(clients):
    for cl in clients:
        cl.shutdown()


@pytest.mark.timeout(10)
def test_server_sends_new_data_when_it_arrives():
    server, clients = get_server_and_clients(n_clients=2)

    with server:
        server.run()
        start_clients(clients)

        server.put(b"Msg 1\r\n")
        time.sleep(0.25)

        server.put(b"Msg 2\r\n")
        time.sleep(0.25)

        stop_clients(clients)
        server.shutdown()

    expected = [b"Msg 1\r\n", b"Msg 2\r\n"]
    assert list(clients[0].data_queue.queue) == expected
    assert list(clients[1].data_queue.queue) == expected


@pytest.mark.timeout(10)
def test_all_new_data_is_sent():
    server, [client] = get_server_and_clients(port=1233, n_clients=1)

    with server:
        server.run()
        client.connect()
        client.run(daemon=True)

        # All data arrives simultaneously
        server.put(b"Msg 1\r\n")
        server.put(b"Msg 2\r\n")
        server.put(b"Msg 3\r\n")

        client.shutdown()
        server.shutdown()

    expected = [b"Msg 1\r\n", b"Msg 2\r\n", b"Msg 3 \r\n"]
    assert list(client.data_queue.queue) == expected


@pytest.mark.timeout(10)
def test_client_disconnects_from_server():
    server, [client] = get_server_and_clients(n_clients=1)
    with server:
        server.run()
        client.connect()
        client.run(daemon=True)

        time.sleep(1)
        client.shutdown()
        server.shutdown()

    assert client.data_queue.empty()


@pytest.mark.timeout(10)
def test_server_keeps_track_of_connected_clients():
    server, [client] = get_server_and_clients(n_clients=1)

    with server:
        server.run()
        client.connect()
        client.run(daemon=True)
        time.sleep(1)

        assert server.n_clients == 1

        new_client = AppClient(server.ip, server.port, logging=False)
        new_client.connect()
        new_client.run(daemon=True)
        time.sleep(0.25)

        assert server.n_clients == 2

        client.shutdown()
        time.sleep(0.25)

        assert server.n_clients == 1

        new_client.shutdown()
        time.sleep(0.25)

        client.shutdown()
        new_client.shutdown()

        assert server.n_clients == 0

        server.shutdown()
