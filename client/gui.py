import Tkinter as tk
import ttk
import tkMessageBox
import operator
import Queue
import os
import sys
import json

from client_comms import Comm
from client_comms import DEFAULT_SERVER_PORT
from client_comms import query_servers
import grid

try:
    import common as cm
except ImportError:
    top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(top_path)
    import common as cm
import gameprotocol as gp


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.queue = Queue.Queue()
        self.c = Comm(self.queue, self)
        self.state = "NO_CONN"

        # <create the rest of your GUI here>
        self.center(650, 800)
        self.v = tk.IntVar()
        self.v2 = tk.IntVar()

        self.ships = {}
        self.servers = query_servers()
        self.choose_server()

    def choose_server(self):
        self.clear()

        title = tk.Label(self, text="Game servers", font=("Helvetica", 16))
        title.pack(side=tk.TOP, fill=tk.X)

        label = tk.Label(self, text="Choose a server to connect to:", anchor=tk.W, font=("Helvetica", 12),
                         padx=15, pady=10)
        label.pack(fill=tk.X)

        for val, server in enumerate(self.servers):
            w = tk.Radiobutton(self, text=server, variable=self.v, value=val, anchor=tk.W,
                               font=("Helvetica", 11), padx=10, pady=10)
            if val == 0:
                w.select()
            w.pack(fill=tk.X)

        okay = tk.Button(self, text="OK", command=lambda: self.callback_server(None), font=("Helvetica", 12), padx=15,
                         pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.destroy, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

        self.bind("<Return>", self.callback_server)  # now you can get to the next stage using Enter

    def choose_nickname(self):
        self.clear()

        title = tk.Label(self, text="Game", font=("Helvetica", 16))
        title.pack(side=tk.TOP, fill=tk.X)
        nickname_label = tk.Label(self, text="Choose your nickname. It should be 4-28 characters long:",
                                  anchor=tk.W, font=("Helvetica", 12),
                                  padx=15, pady=10)
        nickname_label.pack(fill=tk.X)

        nickname = tk.Entry(self, width=30)
        nickname.pack(anchor=tk.W, padx=15, pady=10)
        nickname.focus()

        okay = tk.Button(self, text="OK", command=lambda: self.callback_nickname(None, nickname.get()),
                         font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.choose_server, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

        self.bind("<Return>", lambda e: self.callback_nickname(e, nickname.get()))

    def choose_game(self):
        self.clear()

        title = tk.Label(self, text="Games", font=("Helvetica", 16))
        title.pack(side=tk.TOP, fill=tk.X)
        label = tk.Label(self, text="Choose a game or start a new game:", anchor=tk.W, font=("Helvetica", 12),
                         padx=15, pady=10)
        label.pack(fill=tk.X)

        for val, game in enumerate(self.games):
            w = tk.Radiobutton(self, text=game, variable=self.v2, value=val, anchor=tk.W,
                               font=("Helvetica", 11), padx=10, pady=10)
            if val == 0:
                w.select()
            w.pack(fill=tk.X)

        new_game = tk.Radiobutton(self, text="New game", variable=self.v2, value=(len(self.games)), anchor=tk.W,
                                  font=("Helvetica", 11), padx=10, pady=10)
        new_game.pack(fill=tk.X)
        okay = tk.Button(self, text="OK", command=lambda: self.callback_game(None, self.games, self.v2.get()),
                         font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.choose_server, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

        self.bind("<Return>", lambda e: self.callback_game(e, self.games, self.v2.get()))

    def show_grids(self):
        self.clear()

        self.state = "NO_START_GAME"

        name = self.game.game_id
        title = tk.Label(self, text=str(name), font=("Helvetica", 16))
        title.grid(row=0, columnspan=2)

        self.labels = []

        self.my_grid = grid.GridFrame(master=self, size=self.size, mine=True)
        self.my_grid.grid(row=1, column=0)
        self.opp1_grid = grid.GridFrame(master=self, size=self.size, mine=False)
        self.opp1_grid.grid(row=1, column=1)
        self.labels.append(self.opp1_grid.label)
        self.opp2_grid = grid.GridFrame(master=self, size=self.size, mine=False)
        self.opp2_grid.grid(row=3, column=0)
        self.labels.append(self.opp2_grid.label)
        self.opp3_grid = grid.GridFrame(master=self, size=self.size, mine=False)
        self.opp3_grid.grid(row=3, column=1)
        self.labels.append(self.opp3_grid.label)

        start_button = tk.Button(self, text="Start game", padx=10, pady=20,
                                 command=lambda: self.start_game(start_button))

        for ship, value in self.ships.items():
            ship_size = self.game.identifier.get(ship)[1]
            if value[2]:
                for i in range(ship_size):
                    self.my_grid.gridp.itemconfig(self.my_grid.gridp.rect[value[0], value[1] + i], fill="blue")
            else:
                for i in range(ship_size):
                    self.my_grid.gridp.itemconfig(self.my_grid.gridp.rect[value[0] + i, value[1]], fill="blue")

        if self.nickname == self.game.master:
            start_button.grid(row=6, columnspan=2)
        else:
            self.process_incoming()

    def start_game(self, start_button):
        start_button.destroy()
        self.c.query_start_game(self.game.game_id)

    def change_names(self, opponents):
        j = 0
        for i in range(len(opponents)):
            if opponents[i] != self.nickname:
                self.labels[j].config(text=opponents[i])
                j += 1

    def shooting_frame(self, opponents):
        w1 = tk.Frame(self)
        shoot_opp1_label = tk.Label(w1, text="Coordinates (A,0)", font=("Helvetica", 12), padx=10)
        self.opp1_shoot = tk.Entry(w1, width=10)
        shoot_opp1_label.grid(row=0, column=0)
        self.opp1_shoot.grid(row=0, column=1)
        w1.grid(row=2, column=1)

        w2 = tk.Frame(self)
        shoot_opp2_label = tk.Label(w2, text="Coordinates (A,0)", font=("Helvetica", 12), padx=10)
        self.opp2_shoot = tk.Entry(w2, width=10)
        shoot_opp2_label.grid(row=0, column=0)
        self.opp2_shoot.grid(row=0, column=1)
        w2.grid(row=4, column=0)

        w3 = tk.Frame(self)
        shoot_opp3_label = tk.Label(w3, text="Coordinates (A,0)", font=("Helvetica", 12), padx=10)
        self.opp3_shoot = tk.Entry(w3, width=10)
        shoot_opp3_label.grid(row=0, column=0)
        self.opp3_shoot.grid(row=0, column=1)
        w3.grid(row=4, column=1)

        if len(opponents) - 1 < 2:
            self.disable_grid(w2)
            self.disable_grid(w3)
        elif len(opponents) - 1 < 3:
            self.disable_grid(w3)

        self.shoot_button = tk.Button(self, text="Shoot", command=lambda: self.shoot(None), padx=30, pady=10)
        self.shoot_button.grid(row=8, columnspan=2)

        self.bind("<Return>", self.shoot)

    def disable_grid(self, g):
        for child in g.winfo_children():

            child.configure(state='disable')

    def destroy_shoot(self):
        self.opp1_shoot.destroy()
        self.opp2_shoot.destroy()
        self.opp3_shoot.destroy()
        self.shoot_button.destroy()

    def shoot(self, event):
        coords = {self.opp1_grid.label.cget("text"): self.opp1_shoot.get()}

        if self.opp2_shoot.cget('state') != 'disabled':
            coords[self.opp2_grid.label.cget("text")] = self.opp2_shoot.get()
        if self.opp3_shoot.cget('state') != 'disabled':
            coords[self.opp3_grid.label.cget("text")] = self.opp3_shoot.get()

        for key, val in coords.items():
            if not val:
                tkMessageBox.showwarning("Warning", "You have to fill all the fields.")
                return

        for key, val in coords.items():
            parts = val.split(",")
            process_x = self.game._process_coords(parts[0].upper())
            if process_x[0]:
                coords[key] = (int(process_x[1]), int(parts[1]))
            else:
                tkMessageBox.showwarning("Warning", "No such coordinate exists.")
                return

        self.c.query_shoot(coords, self.nickname, self.game.game_id)

    def show_hits(self, msg):
        shots = msg['shots_fired']
        origin = msg['origin']
        lost_ships = msg['ships_lost']

        for player, v in shots.items():
            if self.nickname == origin:
                if self.opp1_grid.label.cget('text') == player:
                    self.mark_hit_or_miss(v, self.opp1_grid)
                    self.mark_lost_ships(lost_ships, self.opp1_grid)
                if self.opp2_grid.label.cget('text') == player:
                    self.mark_hit_or_miss(v, self.opp2_grid)
                    self.mark_lost_ships(lost_ships, self.opp2_grid)
                if self.opp3_grid.label.cget('text') == player:
                    self.mark_hit_or_miss(v, self.opp3_grid)
                    self.mark_lost_ships(lost_ships, self.opp3_grid)
            elif self.nickname == player and v[-1]:
                self.my_grid.gridp.itemconfig(self.my_grid.gridp.rect[v[0], v[1]], fill="red")

            if self.opp1_grid.label.cget('text') == player:
                self.mark_lost_ships(lost_ships, self.opp1_grid)
            if self.opp2_grid.label.cget('text') == player:
                self.mark_lost_ships(lost_ships, self.opp2_grid)
            if self.opp3_grid.label.cget('text') == player:
                self.mark_lost_ships(lost_ships, self.opp3_grid)

        self.update()

    def mark_lost_ships(self, lost_ships, opp_grid):
        if lost_ships:
            for player, ship in lost_ships.items():
                if self.nickname != player:
                    ship_size = self.game.identifier.get(ship)[1]
                    x = self.ships.get(ship)[0]
                    y = self.ships.get(ship)[1]
                    position = self.ships.get(ship)[-1]

                    if position:
                        for i in range(ship_size):
                            opp_grid.gridp.itemconfig(opp_grid.gridp.rect[x, y + i], fill="red")
                    else:
                        for i in range(ship_size):
                            opp_grid.gridp.itemconfig(opp_grid.gridp.rect[x + i, y], fill="red")

    def mark_hit_or_miss(self, v, opp_grid):
        if not v[-1]:
            opp_grid.gridp.itemconfig(opp_grid.gridp.rect[v[0], v[1]], fill="dim gray")
        else:
            opp_grid.gridp.itemconfig(opp_grid.gridp.rect[v[0], v[1]], fill="red")

    def center(self, width, height):
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def callback_server(self, event):
        host = self.servers[self.v.get()]
        self.c.connect_to_server(host, DEFAULT_SERVER_PORT)
        self.state = "NO_NICK"
        # TODO: siia if-else'id, kui serveriga ei saa yhendust
        self.choose_nickname()

    def callback_nickname(self, event, nickname):
        if not nickname:
            tkMessageBox.showwarning("Warning", "Please choose a nickname to proceed!")
        if len(nickname) < 4 or len(nickname) > 28:
            tkMessageBox.showwarning("Warning", "Length should be between 4-28.")
        if "$" in nickname:
            tkMessageBox.showwarning("Warning", "Please don't use the dollar sign in nickname.")
        else:
            self.c.query_nick(nickname)

    def callback_game(self, event, games, b):
        if b <= len(games) - 1:
            self.joining_game_id = b
            self.c.join_game(games[b])
            self.state = "NO_JOIN"
        else:
            self.choose_grid = tk.Toplevel(self)
            self.choose_grid.title("Choose the grid size")
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.choose_grid.geometry("250x100+%d+%d" % ((w - 250) / 2, (h - 100) / 2))

            tk.Label(self.choose_grid, text="Grid size", padx=5, pady=5).pack()

            e = tk.Entry(self.choose_grid, width=15)
            e.pack(padx=5, pady=5)
            e.focus()

            b = tk.Button(self.choose_grid, text="OK", command=lambda: self.ok(None, e))
            b.pack(pady=5, padx=5)

            self.choose_grid.bind("<Return>", lambda event: self.ok(event, e))

            self.wait_window(self.choose_grid)

    def init_board(self, gid, game_master):
        self.game = gp.GameProtocol(game_id=gid, size=self.size, client_nick=self.nickname, master=game_master)

    def ok(self, event, e):
        self.size = e.get()

        if self.size and self.size.isdigit():
            self.size = int(self.size)
            self.state = "NO_YOUR_GAME"
            self.c.create_game(self.size)
        else:
            tkMessageBox.showwarning("Warning", "You should enter a valid grid size.")
            self.choose_grid.lift()

    def choose_ships(self):
        self.clear()
        self.my_grid = grid.Grid(self, self.size)
        tk.Label(self, text="Place your ships", font=("Helvetica", 16)).grid(row=0, columnspan=2)
        self.my_grid.grid(row=1, column=0)

        w = tk.Frame(self)
        start_point_label = tk.Label(w, text="Starting point (A,0):")
        start_point_label.grid(row=0, column=1)
        direction_label = tk.Label(w, text="Direction:")
        direction_label.grid(row=0, column=2)

        choices = ['Horizontal', 'Vertical']
        ships = {'Carrier': 5, 'Battleship': 4, 'Cruiser': 3, 'Submarine': 3, 'Destroyer': 2}
        i = 1
        for ship, value in sorted(ships.items(), key=operator.itemgetter(1), reverse=True):
            text = ship + " - size " + str(value)
            label = tk.Label(w, text=text, font=("Helvetica", 12), padx=10, pady=10)
            label.grid(row=i, column=0)

            start_point = tk.Entry(w, width=10, font=("Helvetica", 12))
            start_point.grid(row=i, column=1)

            direction = ttk.Combobox(w, values=choices, font=("Helvetica", 12), width=15)
            direction.set("Horizontal")
            direction.state(['readonly'])
            direction.grid(row=i, column=2)

            self.ships[ship] = (start_point, direction)
            i += 1

        w.grid(row=2, column=0, sticky="N")

        okay = tk.Button(self, text="OK", command=lambda: self.send_ships(None), font=("Helvetica", 12), padx=15,
                         pady=10)
        okay.grid(row=3, column=2, sticky="SE", padx=5, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.choose_game, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.grid(row=3, column=1, sticky="SE", padx=5, pady=15)

        self.bind("<Return>", self.send_ships)

    def send_ships(self, event):
        msg = self.check_ships()
        while not msg:
            return

        process_ships = self.game.place_ships(msg)
        if not process_ships:
            tkMessageBox.showwarning("Warning", "Ships didn't fit.")
            return
        else:
            self.c.query_place_ships(self.game.game_id, process_ships)

    def check_ships(self):
        msg = {}
        for ship, value in self.ships.items():
            if value[0].get() != "":
                msg[ship] = (str(value[0].get()).upper(), str(value[1].get()))
            else:
                tkMessageBox.showwarning("Warning", "Please enter all coordinates.")
                return
        return msg

    def process_incoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0).split(cm.MSG_FIELD_SEP)
                print self.state, str(msg)
                if self.state == "NO_NICK":
                    if msg[0] != cm.RSP_OK:
                        tkMessageBox.showwarning("Warning", "Please choose another nickname to proceed!")
                    else:
                        self.nickname = msg[1]
                        self.c.query_games()
                        self.state = "NO_GAMES"
                elif self.state == "NO_GAMES":
                    if msg[0] == cm.RSP_OK:
                        self.games = eval(msg[1])
                        self.choose_game()
                    else:
                        print("Didn't get response from server about games.")
                elif self.state == "NO_YOUR_GAME":
                    if msg[0] == cm.RSP_OK:
                        self.choose_grid.destroy()
                        self.state = "NO_SHIPS"
                        self.init_board(msg[1], self.nickname)
                        self.choose_ships()
                    else:
                        print("Couldn't choose your game. ")
                        tkMessageBox.showwarning("Warning", "Grid size should be 5-15.")
                        self.state = "NO_GAMES"
                        self.choose_game()
                elif self.state == "NO_JOIN":
                    if msg[0] == cm.RSP_OK:
                        self.state = "NO_SHIPS"
                        msg[1] = eval(msg[1])
                        self.size = int(msg[1][0])
                        self.init_board(self.games[self.joining_game_id], msg[1][1])
                        self.choose_ships()
                    elif msg[0] == cm.RSP_MASTER_JOIN:
                        print "Liitusin siiiin"
                        self.state = "NO_SHIPS"
                        data = json.loads(msg[1])
                        print data
                        self.size = int(data["size"])
                        self.init_board(self.games[self.joining_game_id], data["master"])
                        self.choose_ships()
                    else:
                        tkMessageBox.showwarning("Didn't get grid size from server.")
                        self.state = "NO_GAMES"
                        self.choose_game()
                elif self.state == "NO_SHIPS":
                    if msg[0] == cm.RSP_OK:
                        self.ships = {}
                        self.ships = json.loads(msg[1][0])
                        self.show_grids()
                    elif msg[0] == cm.RSP_MASTER_JOIN:
                        print "Somebody joined, WOHOOO"
                        data = json.loads(msg[1])
                        if data[0]["master"] == self.nickname:
                            print "Vaheta nimi ara 2222"
                            self.change_names(json.loads(msg[2]))
                        else:
                            self.state = "NO_START_GAME"
                            self.choose_ships()
                    else:
                        print("Didn't position ships.")
                        self.state = "NO_YOUR_GAME"
                        self.choose_ships()
                elif self.state == "NO_START_GAME":
                    if msg[0] == cm.RSP_MULTI_OK:
                        self.opponents = eval(msg[1])
                        self.change_names(self.opponents)
                        self.state = "START_GAME"
                        if self.game.master == self.nickname:
                            self.shooting_frame(self.opponents)
                    elif msg[0] == cm.RSP_MASTER_JOIN:
                        print "Somebody joined when I was already wanting to start"
                        resp = json.loads(msg[1])
                        if resp["master"] == self.nickname:
                            print "Vaheta nimi ara."
                        else:
                            self.state = "NO_YOUR_GAME"
                            self.choose_ships()
                    else:
                        tkMessageBox.showwarning("Warning", "Sorry, wait for opponents. ")
                        self.show_grids()
                elif self.state == "START_GAME":
                    if msg[0] == cm.RSP_MULTI_OK:
                        extra = json.loads(msg[1])
                        if self.nickname == extra["next"]:
                            self.shooting_frame(self.opponents)
                        if self.nickname == extra["origin"]:
                            self.destroy_shoot()
                            self.show_hits(extra)
                        else:
                            self.show_hits(extra)
                    else:
                        print("Something went wrong from getting shots fired.")

            except Queue.Empty:
                pass


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

    # Close socket when client closes window
    # app.c.sock.close()
    # TODO: close the script somehow?

# TODO: if you get a hit, you can keep shooting at that player's ships - server-side
# TODO: show opponent's name/notify master when somebody joins game
# TODO: master cannot start game before all the opponents have placed ships
# TODO: show who hit you when hit
# TODO: if any ships sinking, all should see
# TODO: whn you lost -> possibility to leave OR possibility for spectator mode
# TODO: if master leaves, random new master
# TODO: if only one player and he leaves, delete the game
# TODO: if you leave (cancel the main gui window), remove your ships from the game
# TODO: games page reloads after entering wrong grid size - maybe fix?
# TODO: fix color code (mark_lost_ships)
