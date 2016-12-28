import logging
import os
import sys
import threading
import pika
import time
import uuid

try:
    import common as cm
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    import common as cm
import json

"""
Responsible for client side communication between user and server
Should make it use RPC and Rabbit
Changelog:
Andre - reworked updates, so everything will be called from common, like cm.RSP_OK (Easier to update code, if changes
        in common happen or something changed)

Authors: Andre & Sander & Annika
"""

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49997
DEFAULT_BUFFER_SIZE = 1024 * 1024

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
LOG = logging.getLogger()


class Comm:
    def __init__(self, queue, master):
        LOG.info("Client started.")
        self.queue = queue
        self.gui = master
        self.running = True

        self.thread1 = threading.Thread(target=self.worker_thread)
        self.thread2 = threading.Thread(target=self.keepalive_thread)
        self.thread3 = threading.Thread(target=self.connection_thread)

        # Python program exits when only "daemonic" threads are left
        self.thread1.daemon = True
        self.thread2.daemon = True
        self.thread3.daemon = True

    def connect_to_server(self, server_addr):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_addr))

        self.to_server = connection.channel()
        self.to_server.queue_declare(queue='in')

        self.to_server_connection = connection.channel()
        self.to_server_connection.queue_declare(queue='alive_in')

        self.from_server = connection.channel()
        result = self.from_server.queue_declare()
        self.queue_name = result.method.queue
        self.from_server.queue_bind(exchange='out', queue=self.queue_name)

        self.from_server_connection = connection.channel()
        result2 = self.from_server_connection.queue_declare()
        self.queue_name_connection = result2.method.queue
        self.from_server_connection.queue_bind(exchange='alive_out', queue=self.queue_name_connection)

        query_conn = self.prepare_response(cm.QUERY_CONNECTION, self.queue_name, {})
        self.corr_id = str(uuid.uuid4())
        LOG.info("Queue name: %s, corr_id: %s" % (self.queue_name, str(self.corr_id)))
        self.to_server.basic_publish(exchange='', routing_key='in', properties=pika.BasicProperties(reply_to=self.queue_name, correlation_id=self.corr_id), body=query_conn)

        self.periodic_call()
        self.thread1.start()

        self.start_time = time.time()
        self.thread2.start()

        self.thread3.start()

    def callback(self, ch, method, properties, body):
        if properties.correlation_id == self.corr_id:
            print "ID MATCHIVAD!!!"
        self.queue.put(body)

    def stop_the_thread_please(self):
        self.running = False
        resp = self.prepare_response(cm.DISCONNECT, self.queue_name_connection, [])
        self.to_server_connection.basic_publish(exchange='', routing_key='alive_in', body=resp)

    def periodic_call(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.process_incoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        else:
            self.gui.after(100, self.periodic_call)

    def worker_thread(self):
        self.from_server.basic_consume(self.callback, queue=self.queue_name, no_ack=True)
        self.from_server.start_consuming()

    def keepalive_thread(self):
        resp = self.prepare_response(cm.KEEP_ALIVE, self.queue_name_connection, {'client': self.queue_name})
        self.to_server_connection.basic_publish(exchange='', routing_key='alive_in', body=resp)
        while True:
            resp = self.prepare_response(cm.KEEP_ALIVE, self.queue_name_connection, [])
            self.to_server_connection.basic_publish(exchange='', routing_key='alive_in', body=resp)
            LOG.info("Sent keep-alive to server: %s" % resp)
            time.sleep(25.0 - ((time.time() - self.start_time) % 25.0))

    def connection_thread(self):
        self.from_server_connection.basic_consume(self.connection_callback, queue=self.queue_name_connection,
                                                  no_ack=True)
        self.from_server_connection.start_consuming()

    def connection_callback(self, ch, method, properties, body):
        print "Keep-alive from server: %s" % body

    @staticmethod
    def prepare_response(request_type, client, data):
        msg = {'type': request_type,
               'client_id': client}
        if len(data) > 0:
            msg['data'] = data
        return json.dumps(msg)

    def query_nick(self, nick):
        self.corr_id = str(uuid.uuid4())
        msg = self.prepare_response(cm.QUERY_NICK, self.queue_name, {'nick': nick})
        self.to_server.basic_publish(exchange='', routing_key='in', properties=pika.BasicProperties(
            reply_to=self.queue_name, correlation_id=self.corr_id), body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_NICK])

    def query_place_ships(self, game_id, ships):
        """
        Dictionary of Ships, where key is ship (Carrier, destroyer etc) and
        value is tuple of (int, int, bool), where first two are x and y for
        start location and boolean marks, if ship is placed horizontally
        or vertically
        :param ships: dictionary
        :param game_id: game id
        :return: boolean, true if all ships placed correctly (no overlap), else false
        """
        # ship_dump = json.dumps(ships, encoding='utf-8')
        msg = self.prepare_response(cm.QUERY_PLACE_SHIPS, self.queue_name, {'game_id': game_id, 'ships': ships})
        self.corr_id = str(uuid.uuid4())
        self.to_server.basic_publish(exchange='', routing_key='in', properties=pika.BasicProperties(
            reply_to=self.queue_name, correlation_id=self.corr_id,
        ), body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_PLACE_SHIPS])

    def create_game(self, game_size):
        msg = self.prepare_response(cm.QUERY_NEW_GAME, self.queue_name, {'size': game_size})
        self.corr_id = str(uuid.uuid4())
        self.to_server.basic_publish(exchange='', routing_key='in', properties=pika.BasicProperties(
            reply_to=self.queue_name, correlation_id=self.corr_id,
        ), body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_NEW_GAME])

    def join_game(self, chosen_game_id):
        msg = self.prepare_response(cm.QUERY_JOIN_GAME, self.queue_name, {'game_id': chosen_game_id})
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_JOIN_GAME])

    def query_games(self):
        msg = self.prepare_response(cm.QUERY_GAMES, self.queue_name, {})
        self.corr_id = str(uuid.uuid4())
        self.to_server.basic_publish(exchange='', routing_key='in', properties=pika.BasicProperties(
            reply_to=self.queue_name, correlation_id=self.corr_id), body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_GAMES])

    def query_start_game(self, game_id):
        msg = self.prepare_response(cm.START_GAME, self.queue_name, {'game_id': game_id})
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.START_GAME])

    def query_shoot(self, nick, positions, game_id):
        # the positions should be dictionary nick: coordinate
        result = {"nick": nick,
                  "shots_fired": positions,
                  "game_id": game_id}
        msg = self.prepare_response(cm.QUERY_SHOOT, self.queue_name, result)
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_SHOOT])

    def query_leave(self, game_id):
        msg = self.prepare_response(cm.QUERY_LEAVE, self.queue_name, {'game_id': game_id})
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)


def query_servers():
    # Just a placeholder for now ...
    return ["127.0.0.1", "10.10.10.10"]
