import socket
import threading

from clientserver.tcp.server import TCPServer, socket_receive, socket_send


responses = [[] for ii in range(3)]


def client(ip, port, msg_len, index):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))

        for _ in range(3):
            data = socket_receive(sock, msg_len)
            responses[index].append(data)

            # Confirm that the message arrived
            socket_send(sock, b"RECVD\r\n", msg_len)


def test_server_accepts_and_sends_data_to_multiple_clients():
    ip, port = "localhost", 12341
    server = TCPServer(ip, port, buff_size=5)

    msg_len = 7
    TCPServer.MSG_LEN = msg_len

    server.put(b"Msg 1\r\n")
    server.put(b"Msg 2\r\n")
    server.put(b"Msg 3\r\n")

    threads = []
    with server:
        server.run()

        for ii in range(3):
            threads.append(threading.Thread(target=client, args=(ip, port, msg_len, ii)))
            threads[ii].start()

        for th in threads:
            th.join()

        server.shutdown()

    assert all(len(responses[ii]) == 3 for ii in range(3))
    assert all(responses[jj][0] == b"Msg 1\r\n" for jj in range(3))
    assert all(responses[jj][1] == b"Msg 2\r\n" for jj in range(3))
    assert all(responses[jj][2] == b"Msg 3\r\n" for jj in range(3))


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
