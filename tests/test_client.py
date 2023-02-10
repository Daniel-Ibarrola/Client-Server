import queue
import threading
import socket

from clientserver import TCPClient

SERVER_QUEUE = queue.Queue()


def server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen()

    connection, _ = sock.accept()

    with connection as conn:
        for ii in range(3):
            message = f"msg {ii + 1}"
            conn.sendall(message.encode())
            SERVER_QUEUE.put(conn.recv(2048).decode())


def test_tcp_client():
    ip, port = "localhost", 12345

    server_thread = threading.Thread(target=server, args=(ip, port), daemon=True)
    server_thread.start()

    client = TCPClient(ip, port)
    client.connect()
    client.run(wait=0)

    server_thread.join()
    client.shutdown()

    assert list(client.queue) == ["msg 1", "msg 2", "msg 3"]
    assert not SERVER_QUEUE.empty()
    assert "Hola" in SERVER_QUEUE
