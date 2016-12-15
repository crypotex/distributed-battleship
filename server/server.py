import os
import sys
import socket
import threading
import logging
import json
from argparse import ArgumentParser
from session import Session
from client_class import Client
import pika
try:
    import common as cm
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    import common as cm


TCP_RECIEVE_BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024
# Constants
DEFAULT_BUFFER_SIZE = 1024

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49997

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
LOG = logging.getLogger()


class Server:
    def __init__(self, addr, port):
        LOG.info("Server Started.")

        self.session = Session()

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=addr))
        self.to_server = connection.channel()
        self.to_server.queue_declare(queue='in')

        self.from_server = connection.channel()
        #result = self.from_server.queue_declare(queue='out')
        self.from_server.exchange_declare(exchange='out', type='fanout')

        #self.from_server.queue_bind(exchange='out', queue=result.method.queue)

        self.to_server.basic_consume(self.run_client_thread, queue='in', no_ack=True)

        #print(' [*] Waiting for messages. To exit press CTRL+C')
        self.to_server.start_consuming()

        #self.socket = self.__socket_init(addr, port)
        #self.main_threader()

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

    # def main_threader(self):
    #     #self.socket.listen(5)
    #     while True:
    #         try:
    #             client, address = self.socket.accept()
    #             client.settimeout(7200)
    #
    #             t_name = "%s-%s" % (address[0], address[1])
    #             t_client = Client(ip=address[0], port=address[1], socket=client, nick=t_name)
    #
    #             LOG.info("New client connected, adding to current session %s." % t_name)
    #             print(self.session.clients)
    #
    #             threading.Thread(target=self.run_client_thread, args=(t_client, )).start()
    #
    #         except KeyboardInterrupt:
    #             LOG.exception('Ctrl+C - terminating server')
    #             break
    #     self.socket.close()

    def run_client_thread(self, ch, method, properties, body):
        LOG.info("New CALLBACK initialized with :%s." % str(body))
        resp = self.session.handle_request(body)
        # if resp.startswith(cm.RSP_MULTI_OK) or resp.startswith(cm.RSP_MASTER_JOIN):
        #     nicks = resp.split(cm.MSG_FIELD_SEP)[-1]
        #     real_nicks = json.loads(nicks, encoding='utf-8')
        #     for nick in real_nicks:
        #         self.session.clients[nick].socket.send(resp)
        #         LOG.info("Multi-Response is: %s." % resp)
        # else:
        #     client.socket.send(resp)
        #     LOG.info("Response is: %s." % resp)
        self.from_server.basic_publish(exchange='out', routing_key='', body=resp)

        # while True:
        #     try:
        #         msg = client.socket.recv(DEFAULT_BUFFER_SIZE).decode('utf-8')
        #         LOG.info("Got request with message: %s." % msg)
        #         resp = self.session.handle_request(msg, client)
        #         # This is just a fix for now
        #         if resp.startswith(cm.RSP_MULTI_OK) or resp.startswith(cm.RSP_MASTER_JOIN):
        #             nicks = resp.split(cm.MSG_FIELD_SEP)[-1]
        #             real_nicks = json.loads(nicks, encoding='utf-8')
        #             for nick in real_nicks:
        #                 self.session.clients[nick].socket.send(resp)
        #                 LOG.info("Multi-Response is: %s." % resp)
        #         else:
        #             client.socket.send(resp)
        #             LOG.info("Response is: %s." % resp)
        #
        #     except socket.error as e:
        #         LOG.error("Socket error: %s" % (str(e)))
        #         break
        # if client.socket is not None:
        #     try:
        #         client.socket.close()
        #     except socket.error:
        #         LOG.info("Client %s:%s disconnected." % (client.ip, client.port))
        # if client is not None:
        #     del client


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
