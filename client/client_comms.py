import os
import sys

import logging
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

    def query_nick(self, nick):
        # Just a placeholder for now
        if ':' in nick:
            LOG.error('":" not allowed in nickname.')
            return False
        self.sock.send(cm.MSG_FIELD_SEP.join([cm.QUERY_NICK, nick]))
        LOG.info(cm.CTR_MSGS[cm.QUERY_NICK])
        msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        if msg[0] == cm.RSP_OK:
            LOG.info("Nickname created.")
            return True
        else:
            LOG.error(cm.ERR_MSGS[msg[0]])
            return False

    def query_ships(self, ships):
        """
        Dictionary of Ships, where key is ship (Carrier, destroyer etc) and
        value is tuple of (int, int, bool), where first two are x and y for
        start location and boolean marks, if ship is placed horizontally
        or vertically
        :param ships: dictionary
        :return: boolean, true if all ships placed correctly (no overlap), else false
        """
        ship_dump = json.dumps(ships, encoding='utf-8')
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_SHIPS, ship_dump])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_SHIPS])
        msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        if msg[0] == cm.RSP_OK:
            LOG.info("Ships queried successfully.")
            return True
        else:
            LOG.error(cm.ERR_MSGS[msg[0]])
            print("Response not ok!")
            return False

    # Is expected that server thread already knows who it is talking to, so no need for a nick, if not
    # Then these methods need to have a nick with them
    def create_game(self, game):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_NEW_GAME, game])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_NEW_GAME])
        msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        if msg[0] == cm.RSP_OK:
            LOG.info("Game created successfully.")
            return True
        else:
            LOG.error(cm.ERR_MSGS[msg[0]])
            return False

    def join_game(self, chosen_game_id):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_JOIN_GAME, chosen_game_id])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_JOIN_GAME])
        msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # Expects to receive list of games as a second part of msg
        if msg[0] == cm.RSP_OK:
            LOG.info("Game joined successfully.")
            # Probably needs a game as a second part of message
            return msg[1]
            # If not then:
            # return True
        else:
            LOG.error(cm.ERR_MSGS[msg[0]])
            return False

    def query_games(self):
        msg = cm.MSG_FIELD_SEP.join([cm.QUERY_GAMES])
        self.sock.send(msg)
        LOG.info(cm.CTR_MSGS[cm.QUERY_GAMES])
        msg = self.sock.recv(DEFAULT_BUFFER_SIZE).split(cm.MSG_FIELD_SEP)
        # Expects to receive list of games/gameID-s as a second part of msg
        if msg[0] == cm.RSP_OK:
            LOG.info("Received list of games available for joining.")
            return msg[1]
        else:
            LOG.error(cm.ERR_MSGS[msg[0]])
            return False

    def listen(self):
        # Should remove this as quickly - just to keep the client from terminating
        self.sock.recv(1024)

    def something(self):
        pass


def query_servers():
    # Just a placeholder for now ...
    return ["127.0.0.1", "10.10.10.10"]


# for testing
# c = Comm(DEFAULT_SERVER_INET_ADDR, DEFAULT_SERVER_PORT)
# msg = c.query_nick("Andre2")
# print(msg)
# shipss = {'Carrier': (0, 0, True), 'Battleship': (0, 1, False),
#           'Cruiser': (1, 1, True), 'Submarine': (1, 2, True),
#           'Destroyer': (4, 3, True)}
# msg = c.query_ships(shipss)
# print(msg)
# c.listen()
