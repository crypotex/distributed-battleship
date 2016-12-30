from itertools import chain
from random import randint
from collections import OrderedDict, Counter

__author__ = "Andre and Annika"


class GameProtocol:
    identifier = {"Carrier": (5, 5), "Battleship": (6, 4), "Cruiser": (7, 3), "Submarine": (8, 3), "Destroyer": (9, 2)}
    reverse_identifier = {5: "Carrier", 6: "Battleship", 7: "Cruiser", 8: "Submarine", 9: "Destroyer"}
    im_hit_im_hit = 1
    i_missed = 2

    """
    Turn list is a orderedDict, with key as nick and value as tuple of [status, index], status is 0 for ok, 1 for lost
    and 2 for left/dc
    """

    def __init__(self, game_id, size, master):
        # Master is a client nick
        self.game_id = game_id
        self.size = size
        self.table = {}
        self.master = master
        self.table[master] = [[0 for _ in range(size)] for i in range(size)]
        # Alive ships : dict of nicks, where values are also dicts with every ship, more importantly a tuple
        # (boolean ShipDead, int x coord, int y coord, boolean horizontal or not)
        self.alive_ships = {}
        self.game_started = False
        self.turn_list = OrderedDict([(master, [0, 0])])
        self.current_turn = master
        self.lost_list = []

    def user_join_game(self, client):
        if client in self.table:
            return False
        else:
            self.table[client] = [[0 for _ in range(self.size)] for i in range(self.size)]
            self.turn_list[client] = [0, len(self.turn_list)]
            result = {"size": self.size,
                      "master": self.master,
                      "opponents": self.table.keys()
                      }
            return result

    def user_leave_game(self, client):
        if client not in self.table:
            return False
        else:
            try:
                leaver = self.turn_list[client]

                if leaver[0] == 0:
                    self.turn_list[client][0] = 2
                    self.table.pop(client)

                    if self.current_turn == client:
                        magic = self.turn_list.keys() * 2
                        magic_index = magic.index(client)
                        while magic_index < len(magic) and self.turn_list[magic[magic_index]][0] != 0:
                            magic_index += 1
                        try:
                            self.current_turn = magic[magic_index]
                        except IndexError as ie:
                            result = {'master': self.master,
                                      'opponents': self.table.keys(),
                                      'next': self.current_turn}
                            return result

                elif leaver[0] == 1:
                    pass
                else:
                    print("User already dc-d or left or lost")
                    return False
            except KeyError:
                print("KEYERRORRR")
                return False

            if client == self.master and len(self.table.keys()) >= 1:
                random_id = randint(0, len(self.table.keys()) - 1)
                self.master = self.table.keys()[random_id]

            remaining = Counter(n for n, s in self.turn_list.items() if s[0] == 0)
            if len(remaining) == 0:
                result = {'master': self.master,
                          'opponents': self.table.keys(),
                          'next': self.current_turn,
                          'winner': self.master}
            else:
                result = {'master': self.master,
                          'opponents': self.table.keys(),
                          'next': self.current_turn,
                          'winner': ""}
            return result

    def place_ships(self, client_nick, enc_ships):
        if type(enc_ships) is not dict:
            print("Stop sending me non dictionaries ... I want dict, you send: %s." % str(type(enc_ships)))
            return False
        if len(enc_ships) != 5:
            return False
        elif set(enc_ships.keys()) != set(self.identifier.keys()):
            return False
        else:
            for ship, params in enc_ships.items():
                if not self._process_ship(client_nick, params[0], params[1], params[2], ship):
                    print ship
                    return False
            self.alive_ships[client_nick] = {i: (j[0], j[1], j[2]) for i, j in enc_ships.items()}
            return enc_ships

    def _process_ship(self, client_nick, x, y, horizontal, ship):
        # Direction on horisontaalne
        identifier, ship_length = self.identifier[ship]
        if horizontal:
            if y + ship_length > self.size:
                return False
            for i in range(y, y + ship_length):
                if self.table[client_nick][x][i] != 0:
                    return False
                self.table[client_nick][x][i] = identifier
        else:
            if x + ship_length > self.size:
                return False
            for i in range(x, x + ship_length):
                if self.table[client_nick][i][y] != 0:
                    return False
                self.table[client_nick][i][y] = identifier
        return True

    def start_game(self):
        nicks = self.get_nicks()
        if all([len(self.alive_ships[e]) == 5 for e in self.alive_ships]) and len(self.alive_ships.keys()) == len(
                nicks) and 1 < len(self.table) < 5:
            self.current_turn = self.master
            self.game_started = True
            return nicks
        else:
            return False

    def next_turn(self):
        cur_players = [n for n, s in self.turn_list.items() if s[0] == 0]
        indeks = cur_players.index(self.current_turn) + 1
        if indeks == len(cur_players):
            indeks = 0
        self.current_turn = cur_players[indeks]
        return self.current_turn

    def get_nicks(self):
        return [nick for nick in self.table]

    def shoot_bombs(self, info):
        shooting_gallery = {}
        origin = self.current_turn
        she_dead = {}
        for nick in info:
            if nick in self.lost_list:
                shooting_gallery[nick] = ("He dead",)
            else:
                t_x, t_y = info[nick][0], info[nick][1]
                if self.validate_coord(t_x, t_y):
                    if self.table[nick][t_x][t_y] > 3:
                        shooting_gallery[nick] = (t_x, t_y, True)
                        ship_id = self.table[nick][t_x][t_y]
                        self.table[nick][t_x][t_y] = self.im_hit_im_hit
                        if all(i != ship_id for i in chain(*self.table[nick])):
                            tmp_ship_type = self.reverse_identifier[ship_id]
                            tmp_dead_ship = (tmp_ship_type, self.alive_ships[nick].pop(tmp_ship_type))
                            she_dead[nick] = tmp_dead_ship
                        # if all(i < 4 for i in chain(*self.table[nick])):
                        #    self.lost_list.append(nick)
                        if len(self.alive_ships[nick]) == 0:
                            self.lost_list.append(nick)
                            self.turn_list[nick][0] = 1
                    elif self.table[nick][t_x][t_y] == self.im_hit_im_hit:
                        shooting_gallery[nick] = (t_x, t_y, True)
                    else:
                        shooting_gallery[nick] = (t_x, t_y, False)
                        self.table[nick][t_x][t_y] = self.i_missed
                else:
                    return False

        next_player = self.next_turn()

        result = {"next": next_player,
                  "lost": self.lost_list,
                  "ships_lost": she_dead,
                  "origin": origin,
                  "shots_fired": shooting_gallery}

        remaining = Counter(n for n, s in self.turn_list.items() if s[0] == 0)
        if len(remaining) == 1:
            result['winner'] = remaining.keys()[0]
        else:
            result['winner'] = ""
        return result

    def spectate(self, client):
        if client in self.lost_list:
            result = {'table': self.table,
                      'alive_ships': self.alive_ships}
        else:
            result = None
        return result

    def validate_coord(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return True
        else:
            return False

    def check_client_turn(self, client_nick):
        return client_nick == self.current_turn