from clientserver import TCPClient


def main():
    ip, port = "localhost", 12345
    client = TCPClient(ip, port, logging=True)
    client.connect()

    try:
        client.run(wait=5, forever=True)
    except KeyboardInterrupt:
        client.shutdown()


if __name__ == "__main__":
    main()
