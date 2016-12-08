import os
import sys

import logging
from socket import AF_INET, SOCK_STREAM, socket
try:
    from common import MSG_FIELD_SEP, QUERY_NICK, RSP_OK
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    from common import MSG_FIELD_SEP, QUERY_NICK, RSP_OK

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49995
DEFAULT_BUFFER_SIZE = 1024 * 1024

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Comm:
    def __init__(self, server_addr, port):
        LOG.info("Client started.")
        self.server = server_addr
        self.port = port

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.server, self.port))
        LOG.info("Socket initialized.")

    def query_nick_available(self, nick):
        # Just a placeholder for now
        self.sock.send(MSG_FIELD_SEP.join([QUERY_NICK, nick]))
        msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(MSG_FIELD_SEP)
        print(msg)
        if msg[0] == RSP_OK:
            return msg[1]

    def listen(self):
        # Should remove this as quickly - just to keep the client from terminating
        self.sock.recv(1024)

    def something(self):
        pass


def query_servers():
    # Just a placeholder for now ...
    return ["127.0.0.1", "10.10.10.10"]

#c = Comm(DEFAULT_SERVER_INET_ADDR, DEFAULT_SERVER_PORT)
#msg = c.query_nick_available("Andre")
#print(msg)
#c.listen()
