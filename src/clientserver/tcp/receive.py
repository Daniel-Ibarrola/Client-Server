import socket


def socket_receive(sock: socket.socket, msg_len: int):
    chunks = []
    bytes_recv = 0
    while bytes_recv < msg_len:
        chk = sock.recv(min(msg_len - bytes_recv, 2048))
        if chk == b"":
            raise ConnectionError("Socket disconnected")
        chunks.append(chk)
        bytes_recv += len(chk)
    return b"".join(chunks)
