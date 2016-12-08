import os
import sys
import socket
import threading
import logging
from argparse import ArgumentParser
try:
    from common import MSG_FIELD_SEP, RSP_OK, QUERY_NICK, QUERY_SHIPS, RSP_SHIPS_PLACEMENT, RSP_NICK_EXISTS
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    from common import MSG_FIELD_SEP, RSP_OK, QUERY_SHIPS, QUERY_NICK, RSP_SHIPS_PLACEMENT, RSP_NICK_EXISTS

TCP_RECIEVE_BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024
# Constants
DEFAULT_BUFFER_SIZE = 1024

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49995

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Server:
    def __init__(self, addr, port):
        LOG.info("Server Started.")
        self.socket = self.__socket_init(addr, port)
        self.clients = {}
        self.main_threader()

    @staticmethod
    def __socket_init(server_ip, port):
        """ Socket Initialization """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((server_ip, port))
        except socket.error as e:
            LOG.error("Socket error: %s" % str(e))
            exit(1)
        LOG.info("Socket initialized")
        return s

    def main_threader(self):
        self.socket.listen(5)
        while True:
            try:
                client, address = self.socket.accept()
                client.settimeout(7200)
                threading.Thread(target=self.run_client_thread, args=(client, address)).start()
                self.clients[address] = client
                LOG.info("Current Clients: %s" % str(self.clients))
            except KeyboardInterrupt:
                LOG.exception('Ctrl+C - terminating server')
                break
        self.socket.close()

    def run_client_thread(self, client, address):
        LOG.info("New thread initialized with :%s and %s" % (str(client), address))

        while True:
            try:
                msg = client.recv(DEFAULT_BUFFER_SIZE).decode('utf-8')
                msg = msg.split(MSG_FIELD_SEP)
                # PLace holder so Annika could test name registration while I program server/client comms and protocol
                # Stupid code though...
                if msg[0] == QUERY_NICK:
                    if msg[1] == "Andre":
                        client.send(RSP_NICK_EXISTS)
                    else:
                        client.send(RSP_OK)
                elif msg[0] == QUERY_SHIPS:
                    if len(msg[1]) < 10:
                        client.send(RSP_SHIPS_PLACEMENT)
                    else:
                        client.send(RSP_OK)

            except socket.error as e:
                LOG.error("Socket error: %s" % (str(e)))
                break
        if client is not None:
            try:
                client.close()
            except socket.error:
                LOG.info("Client %s disconnected." % address)
        if address in self.clients:
            del self.clients[address]


if __name__ == "__main__":
    # Parsing arguments
    parser = ArgumentParser()
    parser.add_argument('-H', '--host',
                        help='Server INET address '
                             'defaults to %s' % DEFAULT_SERVER_INET_ADDR,
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p', '--port', type=int,
                        help='Server TCP port, '
                             'defaults to %d' % DEFAULT_SERVER_PORT,
                        default=DEFAULT_SERVER_PORT)

    args = parser.parse_args()

    srvr = Server(args.host, args.port)
    exit(0)
