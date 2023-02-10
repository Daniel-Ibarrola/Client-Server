from clientserver.utils.echo_server import EchoServer
import sys


if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip, port = sys.argv[1], sys.argv[2]
    else:
        ip, port = "127.0.0.1", 12345

    server = EchoServer(ip, port)

    try:
        server.run(forever=True)  # serve forever
    except KeyboardInterrupt:
        server.shutdown()
