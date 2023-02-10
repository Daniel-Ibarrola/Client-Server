# A simple client that receives data and prints it to the console
import socket
import time


def main():
    ip = "127.0.0.1"
    port = 12345

    cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cl_socket.connect((ip, port))
    print(f"Connected to {(ip, port)}")

    # Send an identification message when connected
    msg = "Hola\r\n".encode("utf-8")
    while True:
        try:
            cl_socket.send(msg)
            data = cl_socket.recv(4096)

            if len(data) > 0:
                print(f"Server: {data.decode().rstrip()}")
            time.sleep(3)

        except (ConnectionError, KeyboardInterrupt):
            break

    print("Disconnecting...")


if __name__ == "__main__":
    main()
