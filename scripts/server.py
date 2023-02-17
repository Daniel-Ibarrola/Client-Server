import threading
import time
import socket
import sys


STOP = False


def receive(sock: socket.socket):
    while not STOP:
        msg = sock.recv(1024)
        if msg.decode().strip() == "Hello World":
            print("Client still connected")


def main():
    global STOP

    if len(sys.argv) == 3:
        ip, port = sys.argv[1:]
    else:
        ip, port = "localhost", 12344

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    print("Started server")

    connection, address = server_socket.accept()
    print(f"Connection accepted from {address}")

    receive_thread = threading.Thread(target=receive, args=(connection,))
    receive_thread.start()

    count = 1
    while not STOP:
        try:
            connection.sendall(f"Msg {count}".encode("utf-8"))
        except (ConnectionError, KeyboardInterrupt):
            STOP = True
            break

        count += 1
        time.sleep(5)


if __name__ == "__main__":
    main()
