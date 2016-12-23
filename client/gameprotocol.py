import json
__author__ = "Annika"


class GameProtocol:
    identifier = {"Carrier": (1, 5), "Battleship": (2, 4), "Cruiser": (3, 3), "Submarine": (4, 3), "Destroyer": (5, 2)}

    def __init__(self, game_id, size, client_nick, master):
        self.game_id = game_id
        self.size = size
        self.table = {}
        self.game_started = False
        self.client_nick = client_nick
        self.master = master

        self.table[client_nick] = [[0 for _ in range(size)] for i in range(size)]

    def place_ships(self, ships):
        processed_ships = {}

        if len(ships) != 5:
            return False
        elif set(ships.keys()) != set(self.identifier.keys()):
            return False
        else:
            for ship, params in ships.items():
                if "," not in params[0]:
                    self.table[self.client_nick] = [[0 for _ in range(self.size)] for i in range(self.size)]
                    return False
                else:
                    try:
                        coords = params[0].split(",")
                        if len(coords) != 2 or not coords[0] or not coords[1]:
                            self.table[self.client_nick] = [[0 for _ in range(self.size)] for i in range(self.size)]
                            return False
                        else:
                            coords[1] = int(coords[1])
                    except ValueError:
                        self.table[self.client_nick] = [[0 for _ in range(self.size)] for i in range(self.size)]
                        return False
                processing = self.process_coords(coords[0])
                if processing[0]:
                    coords[0] = processing[1]
                else:
                    print "Coordination processing failed."
                    return False

                if params[1] == "Horizontal":
                    horizontal = True
                else:
                    horizontal = False

                if not self._process_ship(coords[0], coords[1], horizontal, ship):
                    print(ship)
                    self.table[self.client_nick] = [[0 for _ in range(self.size)] for i in range(self.size)]
                    return False
                else:
                    processed_ships[ship] = (coords[0], coords[1], horizontal)
            print self.table
            return processed_ships

    def _process_ship(self, x, y, horizontal, ship):
        # Direction on horisontaalne
        identifier, ship_length = self.identifier[ship]

        if horizontal:
            if y + ship_length > self.size:
                return False
            for i in range(y, y + ship_length):
                if self.table[self.client_nick][x][i] != 0:
                    return False
                self.table[self.client_nick][x][i] = identifier
        else:
            if x + ship_length > self.size:
                return False
            for i in range(x, x + ship_length):
                if self.table[self.client_nick][i][y] != 0:
                    return False
                self.table[self.client_nick][i][y] = identifier

        return True

    def process_coords(self, y):
        if ord(y) < 65 or ord(y) > 80:
            return False, -1
        else:
            new_x = ord(y) - 65
            if new_x < self.size:
                return True, new_x
            else:
                return False, -1

    def start_game(self):
        pass
