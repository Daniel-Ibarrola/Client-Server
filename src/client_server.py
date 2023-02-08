# Program of a client-server. The client receives and process data and the server sends it forward
import queue
import socket
import time
import threading


def encode_message(msg):
    msg += "\r\n"
    return msg.encode("utf-8")


def client_send():
    """ The client sends and "alive" message every 30 seconds.
    """
    global client_socket
    message = encode_message("Hola")
    while True:
        try:
            client_socket.send(message)
            time.sleep(30)
        except ConnectionError:
            print("Client failed to send message")
            break


def client_receive():
    """Client receives data from server and stores it in queue.
    """
    global client_socket, data_queue
    while True:
        try:
            data = client_socket.recv(4096)

            if len(data) == 0:
                time.sleep(1)
                continue

            data_queue.put(data)
            print(data.decode())

        except ConnectionError:
            print("Client failed to receive data.")
            break


def server_forward():
    """ Servers listens for clients binding and sends data forward.
    """
    global data_queue
    server_ip = "127.0.0.1"
    server_port = 12345

    server_socket.bind((server_ip, server_port))
    server_socket.listen()
    connection, address = server_socket.accept()
    print(f"Server accepted connection of {address}")

    with connection:
        while True:
            if not data_queue.empty():
                data = data_queue.get()
                connection.sendall(data)


def main():
    global client_socket, server_socket
    client_ip = '127.0.0.1'
    client_port = 15555

    client_socket.connect((client_ip, client_port))
    print(f'Client connected to {client_ip}:{client_port}')

    t1 = threading.Thread(target=client_send, daemon=True)
    t2 = threading.Thread(target=client_receive, daemon=True)
    t3 = threading.Thread(target=server_forward, daemon=True)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_queue = queue.Queue()
    main()
