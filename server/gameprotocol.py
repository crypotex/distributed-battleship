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

    def user_join_game(self, client):
        if client in self.table:
            return False
        else:
            self.table[client] = [[0 for _ in range(self.size)] for i in range(self.size)]
            return self.size

    def place_ships(self, client_nick, ships):
        enc_ships = json.loads(ships, encoding='utf-8')
        if len(enc_ships) != 5:
            return False
        elif set(enc_ships.keys()) != set(self.identifier.keys()):
            print(ships.keys())
            return False
        else:
            for ship, params in enc_ships.items():
                if not self._process_ship(client_nick, params[0], params[1], params[2], ship):
                    print(ship)
                    return False
            self.alive_ships[client_nick] = {i: True for i in enc_ships.keys()}

            return self.table

    def _process_ship(self, client_nick, x, y, horizontal, ship):
        # Direction on horisontaalne
        identifier, ship_length = self.identifier[ship]
        if horizontal:
            if x + ship_length > self.size:
                return False
            for i in range(x, x + ship_length):
                if self.table[client_nick][i][y] != 0:
                    return False
                self.table[client_nick][i][y] = identifier
        else:
            if y + ship_length > self.size:
                return False
            for i in range(y, y + ship_length):
                if self.table[client_nick][x][i] != 0:
                    return False
                self.table[client_nick][x][i] = identifier
        return True

    def start_game(self, client_nick):
        if all([len(self.alive_ships[e]) == 5 for e in self.alive_ships]):
            data = json.dump([self.table[cl] for cl in self.table if cl != client_nick], encoding='utf-8')
            return data
        else:
            return False

