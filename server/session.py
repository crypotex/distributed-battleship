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
        self.reverse_clients = {}
        self.games = {}

    def new_client(self, client_id):
        if client_id in self.clients:
            return prepare_neg_response(cm.RSP_CONNECTION_FAILED, [client_id])
        else:
            self.clients[client_id] = client_id
            return prepare_response([client_id])

    def assign_nickname(self, client_id, client_nick):
        if client_id in self.clients:
            if client_nick not in self.reverse_clients:
                self.clients[client_id] = client_nick
                self.reverse_clients[client_nick] = client_id
                return prepare_response([client_id], data={"nick": client_nick})
            else:
                return prepare_neg_response(cm.RSP_BAD_NICK, client_id)
        else:
            return prepare_neg_response(cm.RSP_NO_SUCH_CLIENT, client_id)

    def new_game(self, size, master):
        if size < 5 or size > 15:
            return cm.RSP_BAD_SIZE
        elif master not in self.clients:
            return cm.RSP_NO_SUCH_CLIENT
        else:
            gid = str(uuid.uuid4())
            game = GameProtocol(game_id=gid, size=size, master=master)
            self.games[gid] = game
            return "$".join([cm.RSP_OK, master, gid])

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
                    return "$".join([cm.RSP_MULTI_OK, resp, nicks])
                else:
                    return cm.RSP_NOT_IMPLEMENTED_YET
        else:
            return cm.RSP_NO_SUCH_GAME

    def start_game(self, game_id, client):
        if self.games[game_id].master == client:
            resp = self.games[game_id].start_game()
            # Resp in here is just a punch of nicks
            if resp:
                return "$".join([cm.RSP_MULTI_OK, resp])
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
                return "$".join([cm.RSP_MULTI_OK, resp, nicks])
            else:
                return cm.RSP_INVALID_SHOT
        else:
            return cm.RSP_WAIT_YOUR_TURN

    def handle_request(self, msg_json):
        enc_json = json.loads(msg_json, encoding='utf-8')
        try:
            req = enc_json['type']
            client_id = enc_json['client_id']
        except KeyError:
            print("Shitty request, do nothing")
            return
        try:
            if req == cm.QUERY_CONNECTION:
                resp = self.new_client(client_id)
                return resp

            elif req == cm.QUERY_NICK:
                resp = self.assign_nickname(client_id, enc_json['data']['nick'])
                return resp

            elif req == cm.QUERY_GAMES:
                # games = json.dumps([i for i in self.games], encoding='utf-8')
                pass

            elif req == cm.QUERY_NEW_GAME:
                # resp = self.new_game(size=int(extra[0]), master=client)
                pass

            elif req == cm.QUERY_JOIN_GAME:
                # resp = self.join_game(game_id=extra[0], client=client)
                pass

            elif req == cm.QUERY_PLACE_SHIPS:
                """
                resp = self.games[extra[0]].place_ships(client_nick=client, ships=extra[1])
                if resp:
                    return cm.MSG_FIELD_SEP.join([cm.RSP_OK, client, extra[1]])
                else:
                    return cm.RSP_SHIPS_PLACEMENT
                """
                pass

            elif req == cm.START_GAME:
                pass

            elif req == cm.QUERY_SHOOT:
                pass

            else:
                print("No mans land")
                return cm.RSP_NOT_IMPLEMENTED_YET
        except KeyError:
            print("Request has much info, but no data, put everything in data.")
            return prepare_neg_response(req, client_id)


def prepare_response(clients, data=None):
    resp = {"type": cm.RSP_OK,
            "clients": clients, }
    if len(clients) > 1:
        resp["type"] = cm.RSP_MULTI_OK
    if data:
        resp["data"] = data
    return json.dumps(resp, encoding='utf-8')


def prepare_neg_response(resp_type, client):
    resp = {"type": resp_type,
            "clients": [client],
            "msg": cm.ERR_MSGS[resp_type]}
    return json.dumps(resp, encoding='utf-8')


def nick_ok(nick):
    if len(nick) < 4 or len(nick) > 28:
        return False
    else:
        return True
