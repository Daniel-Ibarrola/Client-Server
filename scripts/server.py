import sys
import threading
import time

from clientserver import TCPServer


STOP = False


def simulate_data(server: TCPServer):

    count = 1
    time.sleep(5)  # Wait for server to start
    while not STOP:
        server.put(f"Msg {count}".encode("utf-8"))
        count += 1
        # time.sleep(2)

        for ii in range(3):
            server.put(f"Msg {count}".encode("utf-8"))
            count += 1

        # time.sleep(2)


def main():
    global STOP
    if len(sys.argv) == 3:
        ip, port = sys.argv[1:]
    else:
        ip, port = "localhost", 12345

    server = TCPServer(ip, port, logging=True)
    simulate_thread = threading.Thread(target=simulate_data, args=(server,), daemon=True)
    print("Started TCP server")
    with server:
        server.run(daemon=False)
        simulate_thread.start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            STOP = True
            print("Exiting...")
            server.shutdown()
            simulate_thread.join()

    print("Server shut down")


if __name__ == "__main__":
    main()
