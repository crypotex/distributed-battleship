import os
import sys
import threading
import logging
import json
import time
from argparse import ArgumentParser
from session import Session
import pika
try:
    import common as cm
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    import common as cm
__author__ = "Andre & Annika"


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
        try:
            LOG.info("Server Started.")

            self.session = Session()
            self.im_aliiiiive = True

            self.connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(host=addr, heartbeat_interval=0))
            self.to_server = self.connection.channel()
            self.to_server.queue_declare(queue='in')

            self.to_server_connection = self.connection.channel()
            self.to_server_connection.queue_declare(queue="alive_in")

            self.from_server_alive = self.connection.channel()
            self.from_server_alive.exchange_declare(exchange='alive_out', type="fanout")

            self.thread1 = threading.Thread(target=self.connection_thread)
            self.thread1.daemon = True
            self.thread1.start()

            self.from_server = self.connection.channel()

            self.from_server.exchange_declare(exchange='out', type='direct')

            self.to_server.basic_consume(self.process_message, queue='in', no_ack=True)

            self.to_server.start_consuming()
        except KeyboardInterrupt:
            self.send_shutdown_msg()
            self.to_server.stop_consuming()
        finally:
            time.sleep(4)
            self.connection.close()


    def process_message(self, ch, method, properties, body):
        if self.im_aliiiiive:
            LOG.info("New CALLBACK initialized with :%s." % str(body))
            resp = self.session.handle_request(body)
            enc_resp = json.loads(resp)
            LOG.info("Before sending, got response: %s." % resp)
            if enc_resp['type'] != cm.RSP_NOANSWER:
                if len(enc_resp['clients']) == 1 and properties.reply_to is not None:
                    self.from_server.basic_publish(exchange='out', routing_key=properties.reply_to,
                                                   properties=pika.BasicProperties(
                                                       correlation_id=properties.correlation_id,
                                                   ),
                                                   body=resp)
                    LOG.info("Sent RPC response to %s, msg was: %s." % (properties.reply_to, enc_resp))
                else:
                    for client in enc_resp['clients']:
                        self.from_server.basic_publish(exchange='out', routing_key=client, body=resp)
                        LOG.info("Sent response to %s, msg was: %s." % (client, enc_resp))

    def connection_thread(self):
        self.to_server_connection.basic_consume(self.process_alive_queue_msg, queue="alive_in", no_ack=True)
        self.to_server_connection.start_consuming()


    def process_alive_queue_msg(self, ch, method, properties, body):
        enc_data = json.loads(body, encoding='utf-8')
        cl_id = enc_data['client_id']
        if enc_data['type'] == cm.KEEP_ALIVE:
            try:
                if cl_id in self.session.clients_alive:
                    self.session.clients_alive[cl_id]['timestamp'] = time.time()
                    LOG.info("Updating timestamp for client %s." % cl_id)
                else:
                    self.session.clients_alive[cl_id] = {'q': enc_data['data']['client'], 'timestamp': time.time()}
            except KeyError:
                LOG.error("Something went wrong, should investigate process_alive_queue_msg, msg was %s. " % body)
        elif enc_data['type'] == cm.DISCONNECT:
            LOG.info("Client %s disconnected." % str(cl_id))
            try:
                client = self.session.clients_alive[cl_id]['q']
                if cl_id in self.session.clients_alive:
                    del self.session.clients_alive[cl_id]
                if client in self.session.clients:
                    nickname = self.session.clients.pop(client)
                    if nickname in self.session.reverse_clients:
                        del self.session.reverse_clients[nickname]
            except KeyError:
                LOG.error("Something went wrong, should investigate process_alive_queue_msg, msg was %s." % body)
                pass
        else:
            LOG.info("Unimplemented alive queue msg type: %s. " % enc_data['type'])

    def send_shutdown_msg(self):
        LOG.info("Shutting down server.")
        prep_msg = json.dumps({'type': cm.SERVER_SHUTDOWN}, encoding='utf-8')
        LOG.info("Sending shutdown seq to all clients.")
        self.from_server_alive.basic_publish(exchange='alive_out', routing_key="", body=prep_msg)


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
    #exit(0)
