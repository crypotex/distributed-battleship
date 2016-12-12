import os
import sys

import json
import uuid

from gameprotocol import GameProtocol

try:
    import common as cm
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    import common as cm
__author__ = "Andre"


class Session:
    def __init__(self):
        self.clients = {}
        self.games = {}

    def new_client(self, client):
        if client.nick in self.clients:
            return cm.RSP_NICK_EXISTS
        else:
            self.clients[client.nick] = client
            return cm.RSP_OK

    def new_game(self, size, master):
        if size < 5 or size > 15:
            return cm.RSP_BAD_SIZE
        elif master not in self.clients:
            return cm.RSP_NO_SUCH_CLIENT
        else:
            gid = uuid.uuid4()
            game = GameProtocol(game_id=gid, size=size, master=master)
            self.games[gid] = game
            return cm.RSP_OK

    def join_game(self, game_id, client):
        if game_id in self.games:
            if client not in self.clients:
                return cm.RSP_NO_SUCH_CLIENT
            elif self.games[game_id].game_started:
                return cm.RSP_GAME_STARTED
            else:
                # TODO: Client diconnect handling here maybe ?
                if self.games[game_id].user_join_game(client):
                    return cm.RSP_OK
                else:
                    return cm.RSP_NOT_IMPLEMENTED_YET
        else:
            return cm.RSP_NO_SUCH_GAME

    def handle_request(self, msg, client):
        it = iter(msg.split(cm.MSG_FIELD_SEP))
        req = it.next()
        extra = list(it)

        if req == cm.QUERY_NICK:
            if client.update_nick(extra[0]):
                resp = self.new_client(client)
                return resp
            else:
                return cm.RSP_BAD_NICK

        elif req == cm.QUERY_GAMES:
            games = json.dumps( [i for i in self.games] , encoding='utf-8')
            return cm.MSG_FIELD_SEP.join(cm.RSP_OK, games)

        elif req == cm.QUERY_NEW_GAME:
            resp = self.new_game(size=int(extra[1]), master=client.nick)
            return resp

        elif req == cm.QUERY_JOIN_GAME:
            resp = self.join_game(game_id=extra[0], client=client.nick)
            return resp

        else:
            print("No mans land")
            return cm.RSP_NOT_IMPLEMENTED_YET