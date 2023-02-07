# A simple client that receives data and prints it to the console
import socket


def main():
    ip = "127.0.0.1"
    port = 12345

    cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cl_socket.connect((ip, port))

    while True:
        data = cl_socket.recv(4096)
        print(data.decode())


if __name__ == "__main__":
    main()
