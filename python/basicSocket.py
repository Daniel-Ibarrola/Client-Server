import threading
import time
import datetime
import socket
import sys

def set_display():
    """Function to show/hide text to the console """
    global display_data
    display_data = not display_data

def send_message():
    """Sends  a message every 30 seconds"""
    message = 'Hola' + '\r\n'
    message = message.encode('utf-8')
    global connected
    global client_socket
    while True:
        try:
            client_socket.send(message)
            time.sleep(30)
        except:
            connected = False
            time.sleep(2)

def rcv_message():
    """Receives data from the server."""
    global client_socket
    global counter
    global app
    i = 0
    while True:
        try:
            data = client_socket.recv(4096)

            if (len(data) < 1):
                time.sleep(2)
                continue

            if display_data:
                print(data.decode())

            if 'Hola' in data.decode():
                counter = 0
                continue
            
            if i == 0:
                print(data.decode().rstrip())
                print("\n")
            
        except:
            time.sleep(2)

def watch_dog():
    """Keeps track of the counter variable. If it passes a certain treshold, it raises an alert"""
    global counter
    global connected
    global app
    global connection_failed
    global client_socket

    print(f'IP: {IP}')
    print(f'Puerto: {PORT}\n')
    
    while True:
        # If it doesn't connect at start, try to connect again
        if connection_failed:
             while not connected:
                try:
                    client_socket.connect((IP, PORT))
                    print('Conexión exitosa\n')
                    connected = True
                    break

                except socket.error:
                    time.sleep(4)
                    print('Tratando de Conectar...')

        if counter > 2 and not connected:
            # print('Contador mayor a 2')
            now = datetime.datetime.now()
            alert_message = 'Se perdio la conexión!\nTiempo: {}'.format(now.strftime("%H:%M:%S"))
            print(alert_message)
            counter = 0
            print('\nConexion perdida... reconectando')
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            while not connected:
                try:
                    client_socket.connect((IP, PORT))
                    print('Reconección exitosa')
                    connected = True
                    break

                except socket.error:
                    time.sleep(2)

        time.sleep(30)
        counter += 1
        print(counter)

def main():
    
    t1 = threading.Thread(target=send_message)
    t2 = threading.Thread(target=rcv_message)
    t3 = threading.Thread(target=watch_dog)

    t1.daemon = True
    t2.daemon = True
    t3.daemon = True

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

if __name__ == '__main__':

    IP = '127.0.0.1'
    try:
        PORT = int(sys.argv[1])
    except:
        PORT = 13587

    display_data = False
    counter = 2
    connected = False

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        print('Conexión exitosa')
        connected = True
        connection_failed = False # Variable to know if the socket connected at the start of the program
    except:
        print('Error al conectarse')
        connection_failed = True
        pass

    main()
