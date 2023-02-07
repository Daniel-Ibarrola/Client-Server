import threading
import time
import socket


def create_message(msg):
    msg += "\r\n"
    return msg.encode("utf-8")


def send_message():
    """ Sends  a message every 30 seconds"""
    global client_socket
    message = create_message("Hola")
    while True:
        try:
            client_socket.send(message)
            time.sleep(30)
        except ConnectionError:
            print("Failed to send message")
            break


def rcv_message():
    """Receives data from the server."""
    global client_socket
    while True:
        try:
            data = client_socket.recv(4096)

            if len(data) == 0:
                time.sleep(2)
                continue

            print(data.decode())

        except ConnectionError:
            print("Error when receiving message")
            break


def main():
    global client_socket
    ip = '127.0.0.1'
    port = 15555

    try:
        client_socket.connect((ip, port))
        print(f'Conectado a {ip}:{port}')
    except ConnectionError:
        print('Error al conectarse')

    t1 = threading.Thread(target=send_message, daemon=True)
    t2 = threading.Thread(target=rcv_message, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main()
