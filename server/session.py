import os
import sys

try:
    from common import MSG_FIELD_SEP, RSP_OK, QUERY_NICK, QUERY_SHIPS, RSP_SHIPS_PLACEMENT, RSP_NICK_EXISTS
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    from common import MSG_FIELD_SEP, RSP_OK, QUERY_SHIPS, QUERY_NICK, RSP_SHIPS_PLACEMENT, RSP_NICK_EXISTS


class Session:
    def __init__(self):
        self.clients = {}
        self.games = []

    def new_client(self, client):
        if client.nick in self.clients:
            return False
        else:
            self.clients[client.nick] = client
            return True

    def new_game(self, master):
        game =

