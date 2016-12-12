import json


class GameProtocol:
    identifier = {"Carrier": (1, 5), "Battleship": (2, 4), "Cruiser": (3, 3), "Submarine": (4, 3), "Destroyer": (5, 2)}

    def __init__(self, size, master):
        # Master is a client nick
        self.size = size
        self.table = {}
        self.master = master
        self.table[master] = [[0 for _ in range(size)] for i in range(size)]
        self.game_started = True

    def user_join_game(self, client):
        if client in self.table:
            return False
        else:
            self.table[client] = [[0 for _ in range(self.size)] for i in range(self.size)]
            return self.table

    def place_ships(self, ships):
        enc_ships = json.loads(ships)
        if len(enc_ships) != 5:
            return False
        elif set(ships.keys()) != set(self.identifier.keys()):
            print(ships.keys())
            return False
        else:
            for ship, params in enc_ships.items():
                if not self._process_ship(params[0], params[1], params[2], ship):
                    print(ship)
                    return False

            return self.table

    def _process_ship(self, x, y, horizontal, ship):
        # Direction on horisontaalne
        identifier, ship_length = self.identifier[ship]
        if horizontal:
            if x + ship_length > self.size:
                return False
            for i in range(x, x + ship_length):
                if self.table[i][y] != 0:
                    return False
                self.table[i][y] = identifier
        else:
            if y + ship_length > self.size:
                return False
            for i in range(y, y + ship_length):
                if self.table[x][i] != 0:
                    return False
                self.table[x][i] = identifier
        return True
