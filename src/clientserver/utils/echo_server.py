# A server that receives data from a single client and sends it back
import socket


class EchoServer:
    pass


def main():
    ip = "127.0.0.1"
    port = 12345

    ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssocket.bind((ip, port))
    ssocket.listen()

    connection, address = ssocket.accept()
    print(f"Server accepted connection from {address}")

    with connection:
        while True:
            data = connection.recv(4096)
            connection.sendall(data)

            if len(data) > 0:
                print(f"Client: {data.decode().rstrip()}")


if __name__ == "__main__":
    main()
