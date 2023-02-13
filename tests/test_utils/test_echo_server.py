import socket
from clientserver.utils.echo_server import EchoServer


def client(ip, port, n_msg=1):
    responses = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        for ii in range(n_msg):
            message = f"msg {ii + 1}"
            sock.sendall(message.encode())
            responses.append(sock.recv(2048).decode())

    return responses


def test_echo_server():
    ip, port = "localhost", 12345

    server = EchoServer(ip, port, save_data=True, logging=False)
    server.run()

    responses = client(ip, port, n_msg=3)
    server.shutdown()

    expected_data = ["msg 1", "msg 2", "msg 3"]
    assert server.data == expected_data
    assert responses == expected_data
