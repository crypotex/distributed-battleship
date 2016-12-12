import os
import sys
import socket
import threading
import logging
from argparse import ArgumentParser
from session import Session
from client_class import Client

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
        self.session = Session()
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

                t_name = "%s-%s" % (address[0], address[1])
                t_client = Client(ip=address[0], port=address[1], socket=client, nick=t_name)

                LOG.info("New client connected, adding to current session %s." % t_name)
                print(self.session.clients)

                threading.Thread(target=self.run_client_thread, args=(t_client, )).start()

            except KeyboardInterrupt:
                LOG.exception('Ctrl+C - terminating server')
                break
        self.socket.close()

    def run_client_thread(self, client):
        LOG.info("New thread initialized with :%s." % (str(client)))

        while True:
            try:
                msg = client.socket.recv(DEFAULT_BUFFER_SIZE).decode('utf-8')
                resp = self.session.handle_request(msg, client)
                client.socket.send(resp)
                LOG.info("Got request with message: %s, response is: %s." % (msg, resp))

            except socket.error as e:
                LOG.error("Socket error: %s" % (str(e)))
                break
        if client.socket is not None:
            try:
                client.socket.close()
            except socket.error:
                LOG.info("Client %s:%s disconnected." % (client.ip, client.port))
        if client is not None:
            del client


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