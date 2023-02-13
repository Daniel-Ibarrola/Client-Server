import socket


def socket_send(sock: socket.socket, data: bytes, msg_len: int):
    total_sent = 0
    while total_sent < msg_len:
        sent = sock.send(data[total_sent:])
        if sent == 0:
            raise ConnectionError("Socket disconnected")
        total_sent += sent
