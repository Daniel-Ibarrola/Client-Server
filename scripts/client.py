from clientserver.utils.app_client import AppClient


def main():
    ip, port = "localhost", 12345
    client = AppClient(ip, port, logging=True)
    client.connect()

    try:
        client.run(forever=True)
    except KeyboardInterrupt:
        client.shutdown()


if __name__ == "__main__":
    main()
