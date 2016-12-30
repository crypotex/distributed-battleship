import Tkinter as tk
import ttk
import tkMessageBox
import operator
import Queue
import os
import sys
import json

from client_comms import Comm
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
        self.state = ""

        # <create the rest of your GUI here>
        self.center(650, 800)
        self.v = tk.IntVar()
        self.v2 = tk.IntVar()

        self.opponents = []
        self.nickname = ""

        self.ships = {}
        self.servers = query_servers()
        self.choose_server()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

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

    # TODO: kui nickname valimises ja cancel, siis saada serverisse, et lahkud. sama, kui m2ngu valid
    def clear_server(self):
        self.c.stop_the_thread_please()
        self.choose_server()

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

        self.create_grids()
        if len(self.opponents) > 0:
            self.change_names(self.opponents)

        self.my_grid.grid(row=1, column=0)
        self.opp1_grid.grid(row=1, column=1)
        self.opp2_grid.grid(row=3, column=0)
        self.opp3_grid.grid(row=3, column=1)

        self.start_button = tk.Button(self, text="Start game", padx=10, pady=20,
                                      command=lambda: self.start_game(self.start_button))

        for ship, value in self.ships.items():
            ship_size = self.game.identifier.get(ship)[1]
            if value[2]:
                for i in range(ship_size):
                    self.my_grid.gridp.itemconfig(self.my_grid.gridp.rect[value[0], value[1] + i], fill="peru")
            else:
                for i in range(ship_size):
                    self.my_grid.gridp.itemconfig(self.my_grid.gridp.rect[value[0] + i, value[1]], fill="peru")

        if self.nickname == self.game.master:
            self.start_button.grid(row=6, columnspan=2)
        else:
            self.process_incoming()

    def start_game(self, start_button):
        start_button.destroy()
        self.c.query_start_game(self.game.game_id)
        self.state = "START_GAME"

    def change_names(self, opponents):
        j = 0
        for i in range(len(opponents)):
            if opponents[i] != self.nickname:
                self.labels[j].config(text=opponents[i])
                j += 1
        self.update_idletasks()

    def shooting_frame(self, opponents):
        w1 = tk.Frame(self)
        shoot_opp1_label = tk.Label(w1, text="Coordinates (A,0)", font=("Helvetica", 11), padx=10)
        self.opp1_shoot = tk.Entry(w1, width=17)
        shoot_opp1_label.grid(row=0, column=0)
        self.opp1_shoot.grid(row=1, column=0)
        w1.grid(row=2, column=1)

        w2 = tk.Frame(self)
        shoot_opp2_label = tk.Label(w2, text="Coordinates (A,0)", font=("Helvetica", 11), padx=10)
        self.opp2_shoot = tk.Entry(w2, width=17)
        shoot_opp2_label.grid(row=0, column=0)
        self.opp2_shoot.grid(row=1, column=0)
        w2.grid(row=4, column=0)

        w3 = tk.Frame(self)
        shoot_opp3_label = tk.Label(w3, text="Coordinates (A,0)", font=("Helvetica", 11), padx=10)
        self.opp3_shoot = tk.Entry(w3, width=17)
        shoot_opp3_label.grid(row=0, column=0)
        self.opp3_shoot.grid(row=1, column=0)
        w3.grid(row=4, column=1)

        if self.opp1_grid.label.cget("text") == "Opponent":
            self.disable_grid(w1)
        if self.opp2_grid.label.cget("text") == "Opponent":
            self.disable_grid(w2)
        if self.opp3_grid.label.cget("text") == "Opponent":
            self.disable_grid(w3)

        self.shoot_button = tk.Button(self, text="Shoot", command=lambda: self.shoot(None), padx=30, pady=10)
        self.shoot_button.grid(row=7, columnspan=2, pady=(15, 0))

        self.leave_button = tk.Button(self, text="Leave game", command=lambda: self.leave_game(), padx=20, pady=10)
        self.leave_button.grid(row=8, columnspan=2, pady=(3, 0))

        self.bind("<Return>", self.shoot)

    def leave_game(self):
        if tkMessageBox.askquestion("Warning", "Are you sure you want to leave? Your ships will be removed."):
            self.c.query_leave(self.game.game_id)
            self.state = "NO_GAMES"
            self.game = None
            self.c.query_games()
        else:
            return

    @staticmethod
    def disable_grid(g):
        for child in g.winfo_children():
            child.configure(state='disable')

    def destroy_shoot(self):
        try:
            self.opp1_shoot.destroy()
            self.opp2_shoot.destroy()
            self.opp3_shoot.destroy()
            self.shoot_button.destroy()
        except:
            pass

    def shoot(self, event):
        coords = {}

        if self.opp1_shoot.cget('state') != 'disabled':
            coords[self.opp1_grid.label.cget("text")] = self.opp1_shoot.get()
        if self.opp2_shoot.cget('state') != 'disabled':
            coords[self.opp2_grid.label.cget("text")] = self.opp2_shoot.get()
        if self.opp3_shoot.cget('state') != 'disabled':
            coords[self.opp3_grid.label.cget("text")] = self.opp3_shoot.get()

        if len(coords.keys()) == 0:
            self.shoot_button.destroy()
            return

        for key, val in coords.items():
            if not val:
                tkMessageBox.showwarning("Warning", "You have to fill all the fields.")
                return
            if "," not in val:
                tkMessageBox.showwarning("Warning", "Please enter correct coordinates.")
                return

        msg = self.check_shoot(coords)
        if not msg:
            tkMessageBox.showwarning("Warning", "Please enter correct coordinates.")
            return
        else:
            self.c.query_shoot(self.nickname, msg, self.game.game_id)
            self.state = "SHOOT"

    def check_shoot(self, data):
        msg = {}
        for opponent, value in data.items():
            value = value.split(",")
            if len(value) == 2 and len(value[1]) != 0:
                process_x = self.game.process_coords(value[0].upper())
                if process_x:
                    try:
                        msg[opponent] = (process_x[1], int(value[1]))
                    except ValueError:
                        return
                else:
                    tkMessageBox.showwarning("Warning", "Please enter correct coordinates.")
                    return
        return msg

    def show_hits(self, msg):
        shots = msg['shots_fired']
        origin = msg['origin']
        lost_ships = msg['ships_lost']
        losers = msg['lost']

        for player, v in shots.items():
            if self.nickname == origin:
                if self.opp1_grid.label.cget('text') == player:
                    self.mark_hit_or_miss(v, self.opp1_grid)
                if self.opp2_grid.label.cget('text') == player:
                    self.mark_hit_or_miss(v, self.opp2_grid)
                if self.opp3_grid.label.cget('text') == player:
                    self.mark_hit_or_miss(v, self.opp3_grid)
            elif self.nickname == player and v[-1]:
                self.my_grid.gridp.itemconfig(self.my_grid.gridp.rect[v[0], v[1]], fill="firebrick")
                self.my_grid.update()
                self.shooter = tk.Label(self, text="You got hit by %s!" % origin, fg="firebrick",
                                        font=("Helvetica", 14, "bold"), padx=10, pady=10)
                self.shooter.grid(row=9, columnspan=4)
                self.shooter.after(3500, self.shooter.destroy)

            if lost_ships:
                self.mark_lost_ships(lost_ships)
        if losers and list(set(losers) - set(self.game.losers)):
            self.mark_losers(list(set(losers) - set(self.game.losers)))

    def mark_losers(self, losers):
        for player in losers:
            if self.opp1_grid.label.cget('text') == player:
                self.disable_grid(self.opp1_grid)
            elif self.opp2_grid.label.cget('text') == player:
                self.disable_grid(self.opp2_grid)
            elif self.opp3_grid.label.cget('text') == player:
                self.disable_grid(self.opp3_grid)

            self.shooter = tk.Label(self, text="%s is dead!..LOL" % player, fg="firebrick",
                                    font=("Helvetica", 14, "bold"), padx=10, pady=10)
            self.shooter.grid(row=9, columnspan=4)
            self.shooter.after(3500, self.shooter.destroy)
            self.game.losers.append(player)

        if self.nickname in losers:
            if tkMessageBox.askyesno("Info", "Would you like to stay and spectate?"):
                self.state = "SPECTATE"
                self.c.query_spectate(self.game.game_id)
            else:
                self.c.query_leave(self.game.game_id)
                self.state = "NO_GAMES"
                self.game = None
                self.c.query_games()

    def mark_lost_ships(self, lost_ships):
        r = 10
        for player, ship in lost_ships.items():
            ship_type = ship[0]
            if self.nickname != player:
                ship_size = self.game.identifier.get(ship_type)[1]
                x, y = ship[1][0], ship[1][1]
                direction = ship[1][-1]

                if direction:
                    for i in range(ship_size):
                        if self.opp1_grid.label.cget('text') == player:
                            self.opp1_grid.gridp.itemconfig(self.opp1_grid.gridp.rect[x, y + i], fill="firebrick")
                        elif self.opp2_grid.label.cget('text') == player:
                            self.opp2_grid.gridp.itemconfig(self.opp2_grid.gridp.rect[x, y + i], fill="firebrick")
                        elif self.opp3_grid.label.cget('text') == player:
                            self.opp3_grid.gridp.itemconfig(self.opp3_grid.gridp.rect[x, y + i], fill="firebrick")
                else:
                    for i in range(ship_size):
                        if self.opp1_grid.label.cget('text') == player:
                            self.opp1_grid.gridp.itemconfig(self.opp1_grid.gridp.rect[x + i, y], fill="firebrick")
                        elif self.opp2_grid.label.cget('text') == player:
                            self.opp2_grid.gridp.itemconfig(self.opp2_grid.gridp.rect[x + i, y], fill="firebrick")
                        elif self.opp3_grid.label.cget('text') == player:
                            self.opp3_grid.gridp.itemconfig(self.opp3_grid.gridp.rect[x + i, y], fill="firebrick")

            self.titanic = tk.Label(self, text="%s's %s has been destroyed! Bummer :(" % (player, ship_type),
                                    fg="firebrick", font=("Helvetica", 14, "bold"), padx=10, pady=10)
            self.titanic.grid(row=r, columnspan=4)
            self.titanic.after(3500, self.titanic.destroy)
            r += 1

    @staticmethod
    def mark_hit_or_miss(v, opp_grid):
        if not v[-1]:
            if (v[0], v[1]) not in opp_grid.gridp.shots:
                opp_grid.gridp.itemconfig(opp_grid.gridp.rect[v[0], v[1]], fill="DodgerBlue3")
        else:
            opp_grid.gridp.itemconfig(opp_grid.gridp.rect[v[0], v[1]], fill="firebrick")
            opp_grid.gridp.shots.append((v[0], v[1]))

    def center(self, width, height):
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def callback_server(self, event):
        host = self.servers[self.v.get()]
        self.c.connect_to_server(host)
        self.state = "NO_CONN"
        self.choose_nickname()

    def callback_nickname(self, event, nickname):
        if len(nickname) < 4 or len(nickname) > 28:
            tkMessageBox.showwarning("Warning", "Length should be between 4-28.")
            return
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

            self.choose_grid.bind("<Return>", lambda event2: self.ok(event2, e))

            self.wait_window(self.choose_grid)

    def init_board(self, gid, game_master):
        self.game = gp.GameProtocol(game_id=gid, size=self.size, client_nick=self.nickname, master=game_master)

    def ok(self, event, e):
        self.size = e.get()

        if self.size and self.size.isdigit():
            self.size = int(self.size)
            self.state = "NO_YOUR_GAME"
            self.c.create_game(self.size)

            self.create_grids()
        else:
            tkMessageBox.showwarning("Warning", "You should enter a valid grid size.")
            self.choose_grid.lift()
            return

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
        cancel = tk.Button(self, text="Cancel", command=self.clear_ships, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.grid(row=3, column=1, sticky="SE", padx=5, pady=15)

        self.bind("<Return>", self.send_ships)

    def clear_ships(self):
        self.c.query_leave(self.game.game_id)
        self.game = None
        self.state = "NO_GAMES"
        self.c.query_games()

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
            self.state = "NO_SHIPS"

    def check_ships(self):
        msg = {}
        for ship, value in self.ships.items():
            if value[0].get() != "":
                msg[ship] = (str(value[0].get()).upper(), str(value[1].get()))
            else:
                tkMessageBox.showwarning("Warning", "Please enter all coordinates.")
                return
        return msg

    def create_grids(self):
        self.labels = []

        self.my_grid = grid.GridFrame(master=self, size=self.size, mine=True)
        self.opp1_grid = grid.GridFrame(master=self, size=self.size, mine=False)
        self.opp2_grid = grid.GridFrame(master=self, size=self.size, mine=False)
        self.opp3_grid = grid.GridFrame(master=self, size=self.size, mine=False)

        self.labels.append(self.opp1_grid.label)
        self.labels.append(self.opp2_grid.label)
        self.labels.append(self.opp3_grid.label)

    # Method to change grid names if someone left before a game started
    def change_names_before_start(self):
        opponent_labels = [label.cget('text') for label in self.labels if label.cget('text') != "Opponent"]
        missing = list(set(opponent_labels) - set(self.opponents))
        for m in missing:
            for label in self.labels:
                if label.cget('text') == m:
                    label.configure(text="Opponent")

    def change_names_after_leaving(self):
        opponent_labels = [label.cget('text') for label in self.labels if label.cget('text') != "Opponent"]
        if opponent_labels != self.opponents:
            missing_list = [x for x in opponent_labels if x not in self.opponents]
            for missing in missing_list:
                if self.opp1_grid.label.cget('text') == missing:
                    try:
                        self.opp1_grid.gridp.clear_grid()
                        self.opp1_shoot.configure(state='disabled')
                    except:
                        pass
                if self.opp2_grid.label.cget('text') == missing:
                    try:
                        self.opp2_grid.gridp.clear_grid()
                        self.opp2_shoot.configure(state='disable')
                    except:
                        pass
                if self.opp3_grid.label.cget('text') == missing:
                    try:
                        self.opp3_grid.gridp.clear_grid()
                        self.opp3_shoot.configure(state='disable')
                    except:
                        pass

                self.update_idletasks()
                for j in range(len(self.labels)):
                    if self.labels[j].cget('text') == missing:
                        self.labels[j].configure(text="Opponent")

    def show_ships(self, data):
        table = data['table']
        alive_ships = data['alive_ships']

        for opponent, ships in table.items():
            if opponent == self.opp1_grid.label.cget('text'):
                self.opp1_grid.color_ships(ships)
            elif opponent == self.opp2_grid.label.cget('text'):
                self.opp2_grid.color_ships(ships)
            elif opponent == self.opp3_grid.label.cget('text'):
                self.opp3_grid.color_ships(ships)

    def process_incoming(self):
        while self.queue.qsize():
            try:
                msg = json.loads(self.queue.get(0))
                print self.state, msg
                if len(msg) > 1 and self.c.queue_name in msg['clients']:
                    if self.state == "NO_CONN":
                        self.state = "NO_NICK"
                    elif self.state == "NO_NICK":
                        if msg['type'] != cm.RSP_OK:
                            tkMessageBox.showwarning("Warning", "Please choose another nickname to proceed!")
                        else:
                            self.nickname = msg['data']['nick']
                            self.c.query_games()
                            self.state = "NO_GAMES"
                    elif self.state == "NO_GAMES":
                        if msg['type'] == cm.RSP_OK:
                            self.games = msg['data']
                            self.opponents = []
                            self.choose_game()
                        else:
                            print("Didn't get response from server about games.")
                    elif self.state == "NO_YOUR_GAME":
                        if msg['type'] == cm.RSP_OK or msg['type'] == cm.RSP_MULTI_OK:
                            self.size = msg['data']['size']
                            self.init_board(msg['data']['game_id'], self.nickname)
                            self.create_grids()
                            if msg['type'] == cm.RSP_OK:
                                self.choose_grid.destroy()
                                self.choose_ships()
                            else:
                                self.opponents = msg['data']['opponents']
                        else:
                            print("Couldn't choose your game. ")
                            tkMessageBox.showwarning("Warning", "Grid size should be 5-15.")
                            self.choose_grid.lift()
                            self.state = "NO_GAMES"
                    elif self.state == "NO_JOIN":
                        if msg['type'] == cm.RSP_MULTI_OK:
                            self.size = msg['data']['size']
                            self.opponents = msg['data']['opponents']
                            self.init_board(self.games[self.joining_game_id], msg["data"]["master"])
                            self.create_grids()
                            self.change_names(self.opponents)
                            self.update()
                            self.choose_ships()
                        elif msg['type'] == cm.RSP_NO_SUCH_GAME:
                            tkMessageBox.showwarning("Warning", "This game doesn't exist anymore.")
                            self.state = "NO_GAMES"
                            self.c.query_games()
                        else:
                            tkMessageBox.showwarning("Warning", "Didn't get grid size from server.")
                            self.state = "NO_GAMES"
                            self.c.query_games()
                    elif self.state == "NO_SHIPS":
                        if msg['type'] == cm.RSP_OK:
                            self.ships = {}
                            self.ships = msg['data']
                            self.after(100, self.show_grids())
                        elif msg['type'] == cm.RSP_MULTI_OK:
                            self.opponents = msg['data']['opponents']
                            if msg['data']['master'] == self.nickname:
                                self.change_names(self.opponents)
                                self.update()
                            else:
                                self.game.master = msg['data']['master']
                        else:
                            print("Didn't position ships.")
                            self.state = "NO_YOUR_GAME"
                            self.choose_ships()
                    elif self.state == "NO_START_GAME":
                        if msg['type'] == cm.RSP_MULTI_OK:
                            if msg['data']['type'] == "join":
                                self.opponents = msg['data']['opponents']
                                self.change_names(self.opponents)
                                self.update_idletasks()
                            elif msg['data']['type'] == "leave":
                                if self.game.master != msg['data']['master']:
                                    self.game.master = msg['data']['master']
                                    if self.nickname == self.game.master:
                                        self.start_button.grid(row=6, columnspan=2)
                                self.opponents = msg['data']['opponents']
                                self.change_names_before_start()
                            else:
                                tkMessageBox.showinfo("Info", "Game started. Wait for your turn.")
                                self.state = "SHOOT"
                        elif msg['type'] == cm.RSP_OK:
                            if self.nickname != self.game.master:
                                self.create_grids()
                        else:
                            tkMessageBox.showwarning("Warning", "Sorry, wait for opponents. ")
                            self.show_grids()
                    elif self.state == "START_GAME":
                        if msg['type'] == cm.RSP_MULTI_OK:
                            if msg['data']['type'] == "leave":
                                if self.game.master != msg['data']['master']:
                                    self.game.master = msg['data']['master']
                                self.opponents = msg['data']['opponents']
                                self.change_names_after_leaving()
                            else:
                                for opponent in msg['data']['nicks']:
                                    if opponent not in self.opponents:
                                        self.opponents.append(opponent)
                                if self.game.master == self.nickname:
                                    self.shooting_frame(self.opponents)
                                else:
                                    tkMessageBox.showinfo("Info", "Game started. Wait for your turn.")
                                    self.state = "SHOOT"
                        else:
                            tkMessageBox.showwarning("Warning", "Please wait for other opponents.")
                            self.state = "NO_START_GAME"
                            self.show_grids()
                    elif self.state == "SHOOT":
                        if msg['type'] == cm.RSP_MULTI_OK:
                            if msg['data']['type'] == 'leave':
                                self.game.master = msg['data']['master']
                                self.destroy_shoot()
                                if self.nickname == msg['data']['next']:
                                    self.shooting_frame(self.opponents)
                                if self.opponents != msg['data']['opponents']:
                                    self.opponents = msg['data']['opponents']
                                    self.change_names_after_leaving()
                            else:
                                extra = msg['data']
                                self.show_hits(extra)
                                if extra['winner'] != "":
                                    if self.nickname == extra['origin']:
                                        self.destroy_shoot()
                                    tkMessageBox.showinfo("Info", str(extra['winner']) + " won the game!")
                                else:
                                    if self.nickname == extra["next"]:
                                        self.shooting_frame(self.opponents)
                                    if self.nickname == extra["origin"]:
                                        self.destroy_shoot()
                                        self.update()
                        else:
                            print("Something went wrong from getting shots fired.")
                    elif self.state == "SPECTATE":
                        print "got to spectate mode"
                        print "Data is: ", msg['data']
                        self.show_ships(msg['data'])

                elif msg['type'] == cm.SERVER_SHUTDOWN:
                    self.on_exit(True)
                else:
                    print "process_incoming unimplemented action, message was %s." % msg

            except Queue.Empty:
                pass

    def on_exit(self, server_shutdown=False):
        if self.state == "NO_START_GAME" or self.state == "START_GAME" or self.state == "SHOOT" or \
                        self.state == "NO_SHIPS" or self.state == "NO_YOUR_GAME":
            self.c.query_leave(self.game.game_id)
        self.c.stop_the_thread_please(server_shutdown)
        if server_shutdown:
            tkMessageBox.showinfo("Info", "Server was shutdown.")
        self.destroy()
        print "Beep Beep Beep Beep, Closing the shop!"
        sys.exit(0)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

    # TODO: spectator mode
