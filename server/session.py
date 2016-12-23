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
        self.clients_alive = {}
        self.reverse_clients = {}
        self.games = {}

    def get_client_id_by_nick(self, client_nicks):
        return [self.reverse_clients[client_nick] for client_nick in self.reverse_clients]

    def new_client(self, client_id):
        if client_id in self.clients:
            return prepare_neg_response(cm.RSP_CONNECTION_FAILED, client_id)
        else:
            self.clients[client_id] = client_id
            return prepare_response(client_id)

    def assign_nickname(self, client_id, client_nick):
        if client_id in self.clients:
            if client_nick not in self.reverse_clients:
                self.clients[client_id] = client_nick
                self.reverse_clients[client_nick] = client_id
                return prepare_response(client_id, data={"nick": client_nick})
            else:
                return prepare_neg_response(cm.RSP_BAD_NICK, client_id)
        else:
            return prepare_neg_response(cm.RSP_NO_SUCH_CLIENT, client_id)

    def query_games(self, client_id):
        resp = [game_id for game_id in self.games]
        return prepare_response(client_id, resp)

    def new_game(self, client_id, size):
        if size < 5 or size > 15:
            return prepare_neg_response(cm.RSP_BAD_SIZE, client_id)
        elif client_id not in self.clients:
            return prepare_neg_response(cm.RSP_NO_SUCH_CLIENT, client_id)
        else:
            master_nick = self.clients[client_id]
            gid = str(uuid.uuid4())
            game = GameProtocol(game_id=gid, size=size, master=master_nick)
            self.games[gid] = game
            response = {
                'size': size,
                'master': master_nick,
                'game_id': gid,
            }
            return prepare_response(client_id, data=response)

    def join_game(self, client_id, game_id):
        if game_id in self.games:
            if client_id not in self.clients:
                return prepare_neg_response(cm.RSP_NO_SUCH_CLIENT, client_id)
            elif self.games[game_id].game_started:
                return prepare_neg_response(cm.RSP_GAME_STARTED, client_id)
            else:
                # TODO: Client diconnect handling here maybe ?
                client_nick = self.clients[client_id]
                resp = self.games[game_id].user_join_game(client_nick)
                if resp:
                    clients = self.get_client_id_by_nick(resp["master"]) + [client_id]
                    resp['type'] = "join"
                    resp['game_id'] = game_id
                    return prepare_response(clients, data=resp)
                else:
                    return prepare_neg_response(cm.RSP_NOT_IMPLEMENTED_YET, client_id)
        else:
            return prepare_neg_response(cm.RSP_NO_SUCH_GAME, client_id)

    def start_game(self, client_id, game_id):
        if self.games[game_id].master == self.clients[client_id]:
            # Resp in here is just a punch of nicks
            resp = self.games[game_id].start_game()
            clients = self.get_client_id_by_nick(resp)
            if resp:
                return prepare_response(clients, data={"nicks": resp, 'type': "start"})
            else:
                return prepare_neg_response(cm.RSP_SHIPS_NOT_PLACED, client_id)
        else:
            return prepare_neg_response(cm.RSP_NOT_MASTER, client_id)

    def shots_fired(self, client_id, shots_dict):
        game = self.games[shots_dict["game_id"]]
        if game.check_client_turn(shots_dict["nick"]) and shots_dict["nick"] == self.clients[client_id]:
            resp = game.shoot_bombs(shots_dict['shots_fired'])
            if resp:
                client_ids = self.get_client_id_by_nick(game.get_nicks())
                resp['type'] = 'shoot'
                return prepare_response(client_ids, resp)
            else:
                return prepare_neg_response(cm.RSP_INVALID_SHOT, client_id)
        else:
            return prepare_neg_response(cm.RSP_WAIT_YOUR_TURN, client_id)

    def place_ships(self, client_id, ships_dict):
        if ships_dict['game_id'] in self.games:
            client_nick = self.clients[client_id]
            resp = self.games[ships_dict['game_id']].place_ships(client_nick, ships_dict['ships'])
            if resp:
                return prepare_response(client_id, resp)
            else:
                prepare_neg_response(cm.RSP_SHIPS_PLACEMENT, client_id)
        else:
            prepare_neg_response(cm.RSP_NO_SUCH_GAME, client_id)

    def leave_game(self, client_id, data):
        if data['game_id'] in self.games:
            client_nick = self.clients[client_id]
            resp = self.games[data['game_id']].user_leave_game(client_nick)
            if resp:
                if len(resp['opponents']) == 0:
                    self.games.pop(data['game_id'])
                    return
                clients = self.get_client_id_by_nick(resp['opponents'])
                resp['type'] = 'leave'
                return prepare_response(clients, resp)
            else:
                prepare_neg_response(cm.RSP_LEAVE_GAME, client_id)
        else:
            prepare_neg_response(cm.RSP_NO_SUCH_GAME, client_id)

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
                resp = self.query_games(client_id)
                return resp

            elif req == cm.QUERY_NEW_GAME:
                resp = self.new_game(client_id, enc_json['data']['size'])
                return resp

            elif req == cm.QUERY_JOIN_GAME:
                resp = self.join_game(client_id, enc_json['data']['game_id'])
                return resp

            elif req == cm.QUERY_PLACE_SHIPS:
                resp = self.place_ships(client_id, enc_json['data'])
                return resp

            elif req == cm.START_GAME:
                resp = self.start_game(client_id, enc_json['data']['game_id'])
                return resp

            elif req == cm.QUERY_SHOOT:
                resp = self.shots_fired(client_id, enc_json['data'])
                return resp
            elif req == cm.QUERY_LEAVE:
                resp = self.leave_game(client_id, enc_json['data'])
                return resp

            else:
                print("No mans land")
                return prepare_neg_response(cm.RSP_NOT_IMPLEMENTED_YET, client_id)
        except KeyError:
            print("Request has much info, but no data, put everything in data.")
            return prepare_neg_response(req, client_id)


def prepare_response(clients, data=None):
    if not isinstance(clients, list):
        clients = [clients]
    resp = {"type": cm.RSP_OK,
            "clients": clients, }
    if len(clients) > 1:
        resp["type"] = cm.RSP_MULTI_OK
    if data is not None:
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
