import tkinter as tk
import tkinter.scrolledtext as tkscrolled
import threading
import queue
import time
import datetime
import logging
import socket
import signal
import sys

logger = logging.getLogger(__name__)

# if sys.frozen == "windows_exe":
#     sys.stderr._error = "inhibit log creation"

class QueueHandler(logging.Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = tkscrolled.ScrolledText(master=frame, fg="#FFFCFC", bg="#1F1919")
        self.scrolled_text.grid(row=0, column=0, sticky="nsew")
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)

class OptionsUi:

    def __init__(self, frame):
        self.frame = frame
        # Connection Status
        self.fr_connect = tk.Frame(master=self.frame,  bg="#4B7398")
        # Create a string variable to change label text
        self.status = tk.StringVar()
        self.status.set('Desconectado')
        self.lbl_connect = tk.Label(master=self.fr_connect, textvariable=self.status, bg="#4B7398")
        self.lbl_connect.config(font=("helvetica", 14, "bold"))
        self.canvas_connect = tk.Canvas(master=self.fr_connect, bg="#C91717", width=20, height=20, bd=0, highlightthickness=0)
        self.fr_connect.grid(row=0, column=0, pady=30)
        self.canvas_connect.pack(side=tk.LEFT, padx=5)
        self.lbl_connect.pack(side=tk.LEFT)
        # Checkbox button
        self.check_var = tk.IntVar(value=1)
        self.btn_text = tk.Checkbutton(master=self.frame, text="Ocultar Texto", variable=self.check_var,  bg="#4B7398", command=set_display)
        self.btn_text.grid(row=1, column=0, sticky="w")
        self.btn_text.config(font=("helvetica", 12))
        self.frame.grid(row=0, column=1, sticky="ns", pady=10)



    def recolor(self):
        """Change status and color depending if it is connected or not"""
        # green: #27BA0F
        # red: #C91717
        if self.status.get() == 'Conectado':
            self.status.set('Desconectado')
            self.canvas_connect.config(background='#C91717')
        elif self.status.get() == 'Desconectado':
            self.status.set('Conectado')
            self.canvas_connect.config(background='#27BA0F')

    def change_status(self):
        """Change status to connected after succesfully establishing a connection through the ip and port entrys"""
        self.status.set('Conectado')
        self.canvas_connect.config(background='#27BA0F')

    def blink(self):
        """Change the color of the box to simulate a blinking light"""
        self.canvas_connect.config(background='#4FFF32')
        time.sleep(1)
        self.canvas_connect.config(background='#27BA0F')


class App:

    def __init__(self, root):
        self.root = root
        root.title("Envío Telegram 2.2.1")
        root.configure(background="#4B7398")
        root.rowconfigure(0, minsize=100, weight=1)
        root.columnconfigure(0, minsize=100, weight=1)
        root.columnconfigure(1, minsize=30, weight=1)
        # Frames
        fr_options = tk.Frame(master=root, bg="#4B7398")
        # Initialize all frames
        self.console = ConsoleUi(root)
        self.options = OptionsUi(fr_options)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    def change_color(self):
        self.options.recolor()

    def update_status(self):
        self.options.change_status()

    def blink(self):
        self.options.blink()

    def quit(self, *args):
        self.root.destroy()

def set_display():
    """Function to show/hide text to the console """
    global display_data
    display_data = not display_data

def reconnect(ip, port):
    """Reconnect after changing IP and/or Port"""
    global client_socket
    global app
    global connected
    global counter
    global IP
    global PORT

    IP = ip
    PORT = port

    try:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        pass
    try:
        client_socket.connect((IP, PORT))
        logger.log(logging.INFO, f'Conectado a IP:{IP}\nPuerto:{PORT}')
        app.update_status()
        connected = True
        counter = 0
    except socket.error:
        logger.log(logging.INFO, f'No se pudo establecer la conexión\n')
        connected = False
        counter = 3

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
    while True:
        try:
            data = client_socket.recv(512)

            if (len(data) < 1):
                time.sleep(2)
                continue

            if display_data:
                logger.log(logging.INFO, data.decode())

            if 'Hola' in data.decode():
                counter = 0
                app.blink()
                continue

            logger.log(logging.INFO, data.decode().rstrip())

        except:
            time.sleep(2)

def watch_dog():
    """Keeps track of the counter variable. If it passes a certain treshold, it raises an alert"""
    global counter
    global connected
    global app
    global connection_failed
    global client_socket

    if not connection_failed:
        app.change_color()

    logger.log(logging.INFO, f'IP: {IP}')
    logger.log(logging.INFO, f'Id: {PORT}\n')
    
    if connected:
        logger.log(logging.INFO, 'Conexión exitosa')
    else:
        logger.log(logging.INFO, 'Error al conectarse')

    while True:
        # If it doesn't connect at start, try to connect again
        if connection_failed:
             while not connected:
                try:
                    client_socket.connect((IP, PORT))
                    logger.log(logging.INFO, 'Conexión exitosa\n')
                    connected = True
                    app.change_color()
                    break

                except socket.error:
                    time.sleep(4)
                    logger.log(logging.INFO, 'Tratando de Conectar...')

        if counter > 2 and not connected:
            # print('Contador mayor a 2')
            app.change_color()
            now = datetime.datetime.now()
            alert_message = 'Se perdio la conexión!\nTiempo: {}'.format(now.strftime("%H:%M:%S"))
            logger.log(logging.INFO, alert_message)
            counter = 0
            logger.log(logging.INFO, '\nConexion perdida... reconectando')
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            while not connected:
                try:
                    client_socket.connect((IP, PORT))
                    logger.log(logging.INFO, 'Reconección exitosa')
                    connected = True
                    app.change_color()
                    break

                except socket.error:
                    time.sleep(2)

        time.sleep(30)
        counter += 1
        print(counter)

def main():
    global app
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    app = App(root)

    t1 = threading.Thread(target=send_message)
    t2 = threading.Thread(target=rcv_message)
    t3 = threading.Thread(target=watch_dog)

    t1.daemon = True
    t2.daemon = True
    t3.daemon = True

    t1.start()
    t2.start()
    t3.start()

    app.root.mainloop()
    sys.exit()

if __name__ == '__main__':

    IP = 'racm.cires-ac.mx'
    try:
        PORT = int(sys.argv[1])
    except:
        PORT = 13402

    display_data = False
    counter = 2
    connected = False

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        connected = True
        connection_failed = False # Variable to know if the socket connected at the start of the program
    except:
        logger.log(logging.INFO, 'Error al conectarse')
        connection_failed = True
        pass

    main()
