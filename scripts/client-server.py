from clientserver import TCPServer, TCPClient


def main():
    server_ip, server_port = "localhost", 12345
    client_ip, client_port = "localhost", 12344

    server = TCPServer(server_ip, server_port, logging=True)
    client = TCPClient(client_ip, client_port, server, logging=True)

    client.connect()
    client.run(daemon=True)

    print("Started TCP server")
    with server:
        server.run(daemon=True)
        try:
            server.serve_forever()
            client.join()
        except KeyboardInterrupt:
            print("Exiting...")
            server.shutdown()
            client.shutdown()

    print("Server shut down")


if __name__ == "__main__":
    main()
