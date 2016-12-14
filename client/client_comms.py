import logging
import os
import sys
import threading
from socket import AF_INET, SOCK_STREAM, socket

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
DEFAULT_SERVER_PORT = 49996
DEFAULT_BUFFER_SIZE = 1024 * 1024

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Comm:
    def __init__(self, queue, master):
        LOG.info("Client started.")
        self.queue = queue
        self.gui = master
        self.running = 1

        self.thread1 = threading.Thread(target=self.worker_thread)

    def connect_to_server(self, server_addr, port):
        self.server = server_addr
        self.port = port

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.server, self.port))
        LOG.info("Socket initialized.")
        self.thread1.start()
        self.periodic_call()

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
        self.gui.after(100, self.periodic_call)

    def worker_thread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following 2 lines with the real
            # thing.
            msg = self.sock.recv(DEFAULT_BUFFER_SIZE)
            # print msg
            self.queue.put(msg)

    def query_nick(self, nick):
        # Just a placeholder for now
        if ':' in nick:
            LOG.error('":" not allowed in nickname.')
            return False
        self.sock.send(cm.MSG_FIELD_SEP.join([cm.QUERY_NICK, nick]))
        LOG.info(cm.CTR_MSGS[cm.QUERY_NICK])
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # if msg[0] == cm.RSP_OK:
        #     LOG.info("Nickname created.")
        #     return True
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     return False

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
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # if msg[0] == cm.RSP_OK:
        #     LOG.info("Ships placed successfully.")
        #     return True
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     print("Response not ok!")
        #     return False

    # Is expected that server thread already knows who it is talking to, so no need for a nick, if not
    # Then these methods need to have a nick with them
    def create_game(self, game):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_NEW_GAME, str(game)])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_NEW_GAME])
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # if msg[0] == cm.RSP_OK:
        #     LOG.info("Game created successfully.")
        #     return True, msg[1]
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     return False

    def join_game(self, chosen_game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_JOIN_GAME, chosen_game_id])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_JOIN_GAME])
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # # Expects to receive list of games as a second part of msg
        # if msg[0] == cm.RSP_OK:
        #     LOG.info("Game joined successfully.")
        #     # Probably needs a game as a second part of message
        #     loading = json.loads(msg[1], encoding='utf-8')
        #     size = loading[0]
        #     master = loading[1]
        #     return size, master
        #     # If not then:
        #     # return True
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     return False

    def query_games(self):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_GAMES])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_GAMES])
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # # Expects to receive list of games/gameID-s as a second part of msg
        # if msg[0] == cm.RSP_OK:
        #     LOG.info("Received list of games available for joining.")
        #     return msg[1]
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     return False

    def query_start_game(self, game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.START_GAME, game_id])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.START_GAME])
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # if msg[0] == cm.RSP_MULTI_OK:
        #     LOG.info("Received game info that is being started.")
        #     # Assumes that all info about the game that is to be started will be in msg parts 1-...
        #     return json.loads(msg[1], encoding='utf-8')
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     return False

    def query_shoot(self, positions, nick, game_id):
        # the positions should be dictionary nick: coordinate
        result = {"nick": nick,
                  "shots_fired": positions,
                  "game_id": game_id}
        shooting_dump = json.dumps(result, encoding="utf-8")
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_SHOOT, shooting_dump])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_SHOOT])
        # msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # if msg[0] == cm.RSP_MULTI_OK:
        #     LOG.info("Shot processed successfully.")
        #     return True
        # else:
        #     LOG.error(cm.ERR_MSGS[msg[0]])
        #     return False

    # def listen_shots_fired(self):
    #     self.sock.settimeout(5)
    #     try:
    #         msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
    #         if msg[0] == cm.RSP_MULTI_OK:
    #             return True, json.loads(msg[1], encoding='utf-8')
    #     except timeout:
    #         msg = False
    #     return msg
    #
    # def listen_start_game(self):
    #     self.sock.settimeout(5)
    #     try:
    #         msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
    #         if msg[0] == cm.RSP_MULTI_OK:
    #             LOG.info("Received game info that is being started by master.")
    #             return json.loads(msg[1], encoding='utf-8')
    #     except timeout:
    #         msg = False
    #     return msg

    def something(self):
        pass


def query_servers():
    # Just a placeholder for now ...
    return ["127.0.0.1", "10.10.10.10"]
