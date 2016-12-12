import json

class GameProtocol:
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
        else:
            if "Carrier" in enc_ships:
                pass
            return self.table

    def _process_ship(self, x, y, direction, size):
        return
