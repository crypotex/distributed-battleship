import Tkinter as tk
import ttk
import tkMessageBox
import operator

from client_comms import Comm
from client_comms import DEFAULT_SERVER_PORT
from client_comms import query_servers

import gameprotocol as gp

# http://stackoverflow.com/questions/4781184/tkinter-displaying-a-square-grid
X_OFFSET = 30
Y_OFFSET = 30


class Grid(tk.Canvas):
    def __init__(self, master, size, mine=False):
        tk.Canvas.__init__(self, master)
        if size <= 9:
            self.grid_size = int(size) * 35 + 5
        elif size <= 13:
            self.grid_size = int(size) * 30 + 5
        else:
            self.grid_size = int(size) * 28 + 10  # vv6ib veel muuta, et paremini oleks jaotatud
        self.rows = int(size)
        self.columns = int(size)
        self.cellheight = 25
        self.cellwidth = 25
        self.rect = {}
        self.config(height=self.grid_size, width=self.grid_size)
        self.mine = mine

        self.make_grid()

    def make_grid(self):
        for i in range(self.rows):
            x = 15
            y = i * self.cellheight + Y_OFFSET + 15
            self.create_text(x, y, text=chr(65 + i))

        for j in range(self.columns):
            x = j * self.cellwidth + X_OFFSET + 14
            y = 20
            self.create_text(x, y, text=j)

        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column * self.cellwidth + X_OFFSET
                y1 = row * self.cellheight + Y_OFFSET
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row, column] = self.create_rectangle(x1, y1, x2, y2)

                # self.tag_bind(self.rect[row, column], '<Double-1>', onObjectClick)

                if self.mine:
                    self.itemconfig(self.rect[row, column], tags=self)


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

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

        games = eval(self.c.query_games())

        for val, game in enumerate(games):
            w = tk.Radiobutton(self, text=game, variable=self.v2, value=val, anchor=tk.W,
                               font=("Helvetica", 11), padx=10, pady=10)
            if val == 0:
                w.select()
            w.pack(fill=tk.X)

        new_game = tk.Radiobutton(self, text="New game", variable=self.v2, value=(len(games)), anchor=tk.W,
                                  font=("Helvetica", 11), padx=10, pady=10)
        new_game.pack(fill=tk.X)
        okay = tk.Button(self, text="OK", command=lambda: self.callback_game(None, games, self.v2.get()),
                         font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.choose_server, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

        self.bind("<Return>", lambda e: self.callback_game(e, games, self.v2.get()))

    def show_grids(self):
        self.clear()

        name = self.game.game_id
        title = tk.Label(self, text=str(name), font=("Helvetica", 16))
        title.grid(row=0, columnspan=2)

        my_grid = tk.Label(self, text="My grid", font=("Helvetica", 12))
        my_grid.grid(row=1, column=0)

        self.opp_label = tk.Label(self, text="Opponent 1", font=("Helvetica", 12), pady=10)
        self.opp_label.grid(row=1, column=1)

        for j in range(2):
            self.opp_label = tk.Label(self, text="Opponent " + str(j + 2), font=("Helvetica", 12), pady=10)
            self.opp_label.grid(row=4, column=j)

        self.my_grid = Grid(self, self.size, mine=True)
        self.my_grid.grid(row=2, column=0)

        self.opp1_grid = Grid(self, self.size)
        self.opp1_grid.grid(row=2, column=1)

        self.opp2_grid = Grid(self, self.size)
        self.opp2_grid.grid(row=5, column=0)

        self.opp3_grid = Grid(self, self.size)
        self.opp3_grid.grid(row=5, column=1)

        start_button = tk.Button(self, text="Start game", padx=10, pady=20,
                                 command=lambda: self.start_game(start_button, name))

        if self.nickname == self.game.master:
            start_button.grid(row=6, columnspan=2)

        for ship, value in self.ships.items():
            ship_size = self.game.identifier.get(ship)[1]
            if value[2]:
                for i in range(ship_size):
                    self.my_grid.itemconfig(self.my_grid.rect[value[0], value[1]+i], fill="blue")
            else:
                for i in range(ship_size):
                    self.my_grid.itemconfig(self.my_grid.rect[value[0]+i, value[1]], fill="blue")

    def start_game(self, start_button):
        start_button.destroy()

        w1 = tk.Frame(self)
        shoot_opp1_label = tk.Label(w1, text="Coordinates (A,0)", font=("Helvetica", 12), padx=10)
        self.opp1_shoot = tk.Entry(w1, width=10)
        shoot_opp1_label.grid(row=0, column=0)
        self.opp1_shoot.grid(row=0, column=1)
        w1.grid(row=3, column=1)

        w2 = tk.Frame(self)
        shoot_opp2_label = tk.Label(w2, text="Coordinates (A,0)", font=("Helvetica", 12), padx=10)
        self.opp2_shoot = tk.Entry(w2, width=10)
        shoot_opp2_label.grid(row=0, column=0)
        self.opp2_shoot.grid(row=0, column=1)
        w2.grid(row=7, column=0)

        w3 = tk.Frame(self)
        shoot_opp3_label = tk.Label(w3, text="Coordinates (A,0)", font=("Helvetica", 12), padx=10)
        self.opp3_shoot = tk.Entry(w3, width=10)
        shoot_opp3_label.grid(row=0, column=0)
        self.opp3_shoot.grid(row=0, column=1)
        w3.grid(row=7, column=1)

        # TODO: siin kutsuda v2lja meetod GameProtocolist
        # TODO: vaja kontrollida, mitu vastast on ja siis vastavalt vajadusele m6ned entry'id disable'ida

    def center(self, width, height):
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def callback_server(self, event):
        host = self.servers[self.v.get()]
        self.c = Comm(host, DEFAULT_SERVER_PORT)
        # TODO: siia if-else'id, kui serveriga ei saa yhendust
        self.choose_nickname()

    def callback_nickname(self, event, nickname):
        free = self.c.query_nick(nickname)

        if not nickname:
            tkMessageBox.showwarning("Warning", "Please choose a nickname to proceed!")
        elif not free:
            tkMessageBox.showwarning("Warning", "Please choose another nickname to proceed!")
        else:
            self.nickname = nickname
            self.choose_game()

    def callback_game(self, event, games, b):
        if b <= len(games) - 1:
            resp = self.c.join_game(games[b])
            if resp:
                self.size = int(resp[0])
                self.init_board(games[b], resp[1])
                self.choose_ships()
            else:
                tkMessageBox.showwarning("Didn't get grid size from server.")
        else:
            choose_grid = tk.Toplevel(self)
            choose_grid.title("Choose the grid size")
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            choose_grid.geometry("250x100+%d+%d" % ((w - 250) / 2, (h - 100) / 2))

            tk.Label(choose_grid, text="Grid size", padx=5, pady=5).pack()

            e = tk.Entry(choose_grid, width=15)
            e.pack(padx=5, pady=5)
            e.focus()

            b = tk.Button(choose_grid, text="OK", command=lambda: self.ok(None, choose_grid, e))
            b.pack(pady=5, padx=5)

            choose_grid.bind("<Return>", lambda event: self.ok(event, choose_grid, e))

            self.wait_window(choose_grid)

    def init_board(self, gid, game_master):
        self.game = gp.GameProtocol(game_id=gid, size=self.size, client_nick=self.nickname, master=game_master)

    def ok(self, event, grid_choose, e):
        self.size = e.get()

        if self.size and self.size.isdigit():
            self.size = int(self.size)
            resp = self.c.create_game(self.size)
            if resp:
                grid_choose.destroy()
                self.init_board(resp[1], self.nickname)
                self.choose_ships()
            else:
                tkMessageBox.showwarning("Warning", "Grid size should be 5-15.")
                grid_choose.lift()
        else:
            tkMessageBox.showwarning("Warning", "You should enter a valid grid size.")
            grid_choose.lift()

    def choose_ships(self):
        self.clear()
        self.my_grid = Grid(self, self.size)
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
        msg = {}
        for ship, value in self.ships.items():
            if value[0].get() != "":
                msg[ship] = (str(value[0].get()).upper(), str(value[1].get()))
            else:
                tkMessageBox.showwarning("Warning", "Please enter all coordinates.")
                return
        process_ships = self.game.place_ships(msg)
        if process_ships:
            resp = self.c.query_place_ships(self.game.game_id, process_ships)
            if resp:
                self.ships = {}
                self.ships = process_ships

                self.show_grids()
            else:
                tkMessageBox.showwarning("Warning", "Something went wrong.")
        else:
            tkMessageBox.showwarning("Warning", "Choose your ships correctly.")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

# root = tk.Tk()
# MainApplication(root).pack(side="top", fill="both", expand=False)
# win = MainApplication(root)
# root.mainloop()
