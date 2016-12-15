import logging
import os
import sys
import threading
from socket import AF_INET, SOCK_STREAM, socket, timeout

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

Authors: Andre & Sander
"""

DEFAULT_SERVER_INET_ADDR = '127.0.0.1'
DEFAULT_SERVER_PORT = 49997
DEFAULT_BUFFER_SIZE = 1024 * 1024

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Comm:
    def __init__(self, queue, master):
        LOG.info("Client started.")
        self.queue = queue
        self.gui = master
        self.running = True

        self.thread1 = threading.Thread(target=self.worker_thread)

    def connect_to_server(self, server_addr, port):
        self.server = server_addr
        self.port = port

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.server, self.port))
        LOG.info("Socket initialized.")
        self.thread1.start()
        self.periodic_call()
        # Test different timeouts here... maybe
        self.sock.settimeout(1.0)

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
        try:
            while self.running:
                try:
                    msg = self.sock.recv(DEFAULT_BUFFER_SIZE)
                    self.queue.put(msg)
                except timeout:
                    # print("timeout")
                    pass

        except KeyboardInterrupt:
            print("Exiting")
            self.running = False


    def query_nick(self, nick):
        self.sock.send(cm.MSG_FIELD_SEP.join([cm.QUERY_NICK, nick]))
        LOG.info(cm.CTR_MSGS[cm.QUERY_NICK])

    def query_place_ships(self, game_id, ships):
        """
        Dictionary of Ships, where key is ship (Carrier, destroyer etc) and
        value is tuple of (int, int, bool), where first two are x and y for
        start location and boolean marks, if ship is placed horizontally
        or vertically
        :param ships: dictionary
        :return: boolean, true if all ships placed correctly (no overlap), else false
        """
        ship_dump = json.dumps(ships, encoding='utf-8')
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_PLACE_SHIPS, game_id, ship_dump])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_PLACE_SHIPS])

    # Is expected that server thread already knows who it is talking to, so no need for a nick, if not
    # Then these methods need to have a nick with them
    def create_game(self, game):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_NEW_GAME, str(game)])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_NEW_GAME])

    def join_game(self, chosen_game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_JOIN_GAME, chosen_game_id])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_JOIN_GAME])

    def query_games(self):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_GAMES])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_GAMES])

    def query_start_game(self, game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.START_GAME, game_id])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.START_GAME])

    def query_shoot(self, positions, nick, game_id):
        # the positions should be dictionary nick: coordinate
        result = {"nick": nick,
                  "shots_fired": positions,
                  "game_id": game_id}
        shooting_dump = json.dumps(result, encoding="utf-8")
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_SHOOT, shooting_dump])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_SHOOT])

    def something(self):
        pass


def query_servers():
    # Just a placeholder for now ...
    return ["127.0.0.1", "10.10.10.10"]
