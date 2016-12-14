import json

__author__ = "Andre"


class GameProtocol:
    identifier = {"Carrier": (1, 5), "Battleship": (2, 4), "Cruiser": (3, 3), "Submarine": (4, 3), "Destroyer": (5, 2)}

    def __init__(self, game_id, size, master):
        # Master is a client nick
        self.game_id = game_id
        self.size = size
        self.table = {}
        self.master = master
        self.table[master] = [[0 for _ in range(size)] for i in range(size)]
        self.alive_ships = {}
        self.game_started = False
        self.turn_list = [master]
        self.current_turn = 0

    def user_join_game(self, client):
        if client in self.table:
            return False
        else:
            self.table[client] = [[0 for _ in range(self.size)] for i in range(self.size)]
            self.turn_list.append(client)
            return json.dumps([self.size, self.master], encoding='utf-8')

    def place_ships(self, client_nick, ships):
        enc_ships = json.loads(ships, encoding='utf-8')
        if type(enc_ships) is not dict:
            print("Stop sending me non dictionaries ... I want dict, you send: %s." % str(type(enc_ships)))
            return False
        if len(enc_ships) != 5:
            print(enc_ships)
            return False
        elif set(enc_ships.keys()) != set(self.identifier.keys()):
            print(ships.keys())
            return False
        else:
            print(enc_ships)
            for ship, params in enc_ships.items():
                if not self._process_ship(client_nick, params[0], params[1], params[2], ship):
                    print ship
                    return False
            self.alive_ships[client_nick] = {i: True for i in enc_ships.keys()}

            print(enc_ships)
            return True

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
        if all([len(self.alive_ships[e]) == 5 for e in self.alive_ships]) and 1 < len(self.table) < 5:
            self.current_turn = 0
            return self.get_nicks()
        else:
            return False

    def get_nicks(self):
        return json.dumps([nick for nick in self.table], encoding='utf-8')

    def shoot_bombs(self, info):
        shooting_gallery = {}
        for nick in info:
            t_x, t_y = info[nick][0], info[nick][1]
            if self.validate_coord(t_x, t_y):
                print
                if self.table[nick][t_x][t_y] > 0:
                    shooting_gallery[nick] = (t_x, t_y, True)

                    # TODO: Add sinking checks here
                else:
                    shooting_gallery[nick] = (t_x, t_y, False)
            else:
                return False
        # TODO: Add win/lose checks here

        if self.current_turn == len(self.turn_list) - 1:
            self.current_turn = 0
            next_player = self.turn_list[self.current_turn]
        else:
            self.current_turn += 1
            next_player = self.turn_list[self.current_turn]
        result = {"next": next_player,
                  "shots_fired": shooting_gallery}
        return json.dumps(result, encoding="utf-8")

    def validate_coord(self, x, y):
        if x > -1 or x < self.size or y > -1 or y < self.size:
            return True
        else:
            return False

    def check_client_turn(self, client_nick):
        return client_nick == self.turn_list[self.current_turn]
