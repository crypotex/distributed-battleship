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
        if client in self.clients:
            return cm.RSP_CONNECTION_FAILED
        else:
            self.clients[client] = client
            return cm.MSG_FIELD_SEP.join([cm.RSP_CONNECTION_SUCCESS, client, client])

    def assign_nickname(self, client, queue_name):
        if queue_name in self.clients and client not in self.clients:
            self.clients[client] = self.clients.pop(queue_name)
            return cm.MSG_FIELD_SEP.join([cm.RSP_OK, client, queue_name])
        else:
            return cm.RSP_NO_SUCH_CLIENT

    def new_game(self, size, master):
        if size < 5 or size > 15:
            return cm.RSP_BAD_SIZE
        elif master not in self.clients:
            return cm.RSP_NO_SUCH_CLIENT
        else:
            gid = str(uuid.uuid4())
            game = GameProtocol(game_id=gid, size=size, master=master)
            self.games[gid] = game
            return cm.MSG_FIELD_SEP.join([cm.RSP_OK, master, gid])

    def join_game(self, game_id, client):
        if game_id in self.games:
            if client not in self.clients:
                return cm.RSP_NO_SUCH_CLIENT
            elif self.games[game_id].game_started:
                return cm.RSP_GAME_STARTED
            else:
                # TODO: Client diconnect handling here maybe ?
                resp = self.games[game_id].user_join_game(client)
                if resp:
                    jresp = json.loads(resp, encoding='utf-8')
                    resp = json.dumps(jresp["result"])
                    nicks = json.dumps(jresp["nicks"])
                    return cm.MSG_FIELD_SEP.join([cm.RSP_MASTER_JOIN, resp, nicks])
                else:
                    return cm.RSP_NOT_IMPLEMENTED_YET
        else:
            return cm.RSP_NO_SUCH_GAME

    def start_game(self, game_id, client):
        if self.games[game_id].master == client:
            resp = self.games[game_id].start_game()
            # Resp in here is just a punch of nicks
            if resp:
                return cm.MSG_FIELD_SEP.join([cm.RSP_MULTI_OK, resp])
            else:
                return cm.RSP_SHIPS_NOT_PLACED
        else:
            return cm.RSP_NOT_MASTER

    def shots_fired(self, json_dic):
        enc_dic = json.loads(json_dic, encoding='utf-8')
        game = self.games[enc_dic["game_id"]]
        nicks = game.get_nicks()
        if game.check_client_turn(enc_dic["nick"]):
            resp = game.shoot_bombs(enc_dic['shots_fired'])
            if resp:
                return cm.MSG_FIELD_SEP.join([cm.RSP_MULTI_OK, resp, nicks])
            else:
                return cm.RSP_INVALID_SHOT
        else:
            return cm.RSP_WAIT_YOUR_TURN

    def handle_request(self, msg):
        it = iter(msg.split(cm.MSG_FIELD_SEP))
        req = it.next()
        client = it.next()
        extra = list(it)

        if req == cm.QUERY_NICK:
            if nick_ok(client):
                resp = self.assign_nickname(client, extra[0])
                return resp
            else:
                return cm.RSP_CONNECTION_FAILED

        elif req == cm.QUERY_CONNECTION:
            if nick_ok(client):
                resp = self.new_client(client)
                return resp
            else:
                return cm.RSP_BAD_NICK

        elif req == cm.QUERY_GAMES:
            games = json.dumps([i for i in self.games], encoding='utf-8')
            return cm.MSG_FIELD_SEP.join([cm.RSP_OK, client, games])

        elif req == cm.QUERY_NEW_GAME:
            resp = self.new_game(size=int(extra[0]), master=client)
            return resp

        elif req == cm.QUERY_JOIN_GAME:
            resp = self.join_game(game_id=extra[0], client=client)
            return resp

        elif req == cm.QUERY_PLACE_SHIPS:
            resp = self.games[extra[0]].place_ships(client_nick=client, ships=extra[1])
            if resp:
                return cm.MSG_FIELD_SEP.join([cm.RSP_OK, client, extra[1]])
            else:
                return cm.RSP_SHIPS_PLACEMENT

        elif req == cm.START_GAME:
            resp = self.start_game(game_id=extra[0], client=client)
            return resp

        elif req == cm.QUERY_SHOOT:
            resp = self.shots_fired(extra[0])
            return resp

        else:
            print("No mans land")
            return cm.RSP_NOT_IMPLEMENTED_YET

def nick_ok(nick):
    if len(nick) < 4 or len(nick) > 100:
        return False
    else:
        return True