from clientserver.utils.echo_server import EchoServer
import pytest


def test_echo_server():
    server = EchoServer("localhost", 12345)
    pytest.fail("Implement me!")
