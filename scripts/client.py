from clientserver.utils.app_client import AppClient


def main():
    ip, port = "localhost", 12345
    client = AppClient(ip, port, logging=True, save_data=False)
    client.connect()

    client.run(daemon=False)
    try:
        client.join()
    except KeyboardInterrupt:
        client.shutdown()


if __name__ == "__main__":
    main()
