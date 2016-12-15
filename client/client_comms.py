import logging
import os
import sys
import threading
import pika

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

    def connect_to_server(self, server_addr):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=server_addr))

        self.to_server = connection.channel()
        self.to_server.queue_declare(queue='in')

        self.from_server = connection.channel()
        result = self.from_server.queue_declare(exclusive=True)
        self.queue_name = result.method.queue
        self.from_server.queue_bind(exchange='out', queue=self.queue_name)

        self.periodic_call()
        self.thread1.start()

    def callback(self, ch, method, properties, body):
        self.queue.put(body)

    def stop_the_thread_please(self):
        self.running = False
        self.sock.close()

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
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """

        self.from_server.basic_consume(self.callback, queue=self.queue_name, no_ack=True)
        self.from_server.start_consuming()
        # print "blabla"
        # try:
        #     while self.running:
        #         try:
        #             #msg = self.sock.recv(DEFAULT_BUFFER_SIZE)
        #             LOG.info("Sain serverilt: ")
        #             #msg = self.from_server.start_consuming()
        #             #self.queue.put(body)
        #         except timeout:
        #             # print("timeout")
        #             pass
        #
        # except KeyboardInterrupt:
        #     print("Exiting")
        #     self.running = False

    def query_nick(self, nick):
        self.to_server.basic_publish(exchange='', routing_key='in', body=cm.MSG_FIELD_SEP.join([cm.QUERY_NICK, nick]))
        LOG.info(cm.CTR_MSGS[cm.QUERY_NICK])

    def query_place_ships(self, nick, game_id, ships):
        """
        Dictionary of Ships, where key is ship (Carrier, destroyer etc) and
        value is tuple of (int, int, bool), where first two are x and y for
        start location and boolean marks, if ship is placed horizontally
        or vertically
        :param ships: dictionary
        :return: boolean, true if all ships placed correctly (no overlap), else false
        """
        ship_dump = json.dumps(ships, encoding='utf-8')
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_PLACE_SHIPS, nick, game_id, ship_dump])
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_PLACE_SHIPS])

    def create_game(self, nick, game):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_NEW_GAME, nick, str(game)])
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_NEW_GAME])

    def join_game(self, nick, chosen_game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_JOIN_GAME, nick, chosen_game_id])
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_JOIN_GAME])

    def query_games(self, nick):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_GAMES, nick])
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_GAMES])

    def query_start_game(self, nick, game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.START_GAME, nick, game_id])
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.START_GAME])

    def query_shoot(self, positions, nick, game_id):
        # the positions should be dictionary nick: coordinate
        result = {"nick": nick,
                  "shots_fired": positions,
                  "game_id": game_id}
        shooting_dump = json.dumps(result, encoding="utf-8")
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_SHOOT, nick, shooting_dump])
        self.to_server.basic_publish(exchange='', routing_key='in', body=msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_SHOOT])


def query_servers():
    # Just a placeholder for now ...
    return ["127.0.0.1", "10.10.10.10"]
