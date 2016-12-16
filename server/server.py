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

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=addr))
        self.to_server = self.connection.channel()
        self.to_server.queue_declare(queue='in')

        self.from_server_multi = self.connection.channel()
        #result = self.from_server.queue_declare(queue='out')
        self.from_server_multi.exchange_declare(exchange='multi_out', type='fanout')

        #self.from_server.queue_bind(exchange='out', queue=result.method.queue)

        self.to_server.basic_consume(self.run_client_thread, queue='in', no_ack=True)

        #print(' [*] Waiting for messages. To exit press CTRL+C')
        self.to_server.start_consuming()

        #self.socket = self.__socket_init(addr, port)
        #self.main_threader()

    def run_client_thread(self, ch, method, properties, body):
        LOG.info("New CALLBACK initialized with :%s." % str(body))
        resp = self.session.handle_request(body)
        enc_resp = json.loads(resp)
        #print "Jeeeheee, ", resp
        #print self.session.clients
        LOG.info("Before sending, got response: %s." % resp)
        for client in enc_resp['clients']:
            self.from_server.basic_publish(exchange='out', routing_key=client, body=resp)
            LOG.info("Sent response to %s, msg was: %s." % (client, enc_resp) )

        """
        if enc_resp['type'] == cm.RSP_MULTI_OK:
            #print "Multi-response: ", resp
            self.from_server_multi.basic_publish(exchange='multi_out', routing_key='', body=resp)
            LOG.info("RESPONSE WAS: %s" % resp)
        elif resp.startswith(cm.RSP_CONNECTION_SUCCESS):
            parts = resp.split(cm.MSG_FIELD_SEP)
            #self.from_server.queue_bind(exchange='out', queue=parts[1])
            #print "Connection success ", str(parts[1])
            self.from_server = self.connection.channel()
            #self.from_server.queue_declare(queue=parts[1])
            #self.from_server.exchange_declare(exhange='out', type='direct')
            self.from_server.basic_publish(exchange='out', routing_key=self.session.clients[parts[1]], body=resp)
            LOG.info("RESPONSE WAS: %s" % resp)
        # elif body.startswith(cm.QUERY_NICK):
        #     data = resp.split(cm.MSG_FIELD_SEP)
        #     print "Nyyd olen siin, ", self.session.clients[data[1]]
        #     self.from_server.basic_publish(exchange='out', routing_key=self.session.clients[data[1]], body=resp)

        # if resp.startswith(cm.RSP_MULTI_OK) or resp.startswith(cm.RSP_MASTER_JOIN):
        #     nicks = resp.split(cm.MSG_FIELD_SEP)[-1]
        #     real_nicks = json.loads(nicks, encoding='utf-8')
        #     for nick in real_nicks:
        #         self.session.clients[nick].socket.send(resp)
        #         LOG.info("Multi-Response is: %s." % resp)
        # else:
        #     client.socket.send(resp)
        #     LOG.info("Response is: %s." % resp)
        else:
            #print "Other responses: ", resp
            #print self.session.clients[parts[1]]
            self.from_server.basic_publish(exchange='out', routing_key=enc_resp['clients'][0], body=resp)
            LOG.info("RESPONSE WAS: %s" % resp)
        """

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
