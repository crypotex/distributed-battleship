import Tkinter as tk
from client_comms import query_servers

# http://stackoverflow.com/questions/4781184/tkinter-displaying-a-square-grid
X_OFFSET = 10
Y_OFFSET = 10


class Grid(tk.Canvas):
    def __init__(self, master, size, mine=False):
        tk.Canvas.__init__(self, master)
        self.grid_size = int(size) * 30 + 10  # vv6ib veel muuta, et paremini oleks jaotatud
        self.rows = int(size)
        self.columns = int(size)
        self.cellheight = 25
        self.cellwidth = 25
        self.rect = {}
        self.config(height=self.grid_size, width=self.grid_size)
        self.mine = mine

        self.make_grid()

    def make_grid(self):
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
        self.nickname = tk.Entry(self, width=30)

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

        okay = tk.Button(self, text="OK", command=self.callback_server, font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.destroy, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

    def choose_nickname(self):
        self.clear()

        title = tk.Label(self, text="Game", font=("Helvetica", 16))
        title.pack(side=tk.TOP, fill=tk.X)
        nickname_label = tk.Label(self, text="Choose your nickname:", anchor=tk.W, font=("Helvetica", 12),
                                  padx=15, pady=10)
        nickname_label.pack(fill=tk.X)

        self.nickname = tk.Entry(self, width=30)
        self.nickname.pack(anchor=tk.W, padx=15, pady=10)
        self.nickname.focus()

        okay = tk.Button(self, text="OK", command=self.callback_nickname, font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.choose_server, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

    def choose_game(self):
        self.clear()

        title = tk.Label(self, text="Games", font=("Helvetica", 16))
        title.pack(side=tk.TOP, fill=tk.X)
        label = tk.Label(self, text="Choose a game or start a new game:", anchor=tk.W, font=("Helvetica", 12),
                         padx=15, pady=10)
        label.pack(fill=tk.X)

        # games = query_games()
        games = ["First game", "Second game"]
        for val, game in enumerate(games):
            w = tk.Radiobutton(self, text=game, variable=self.v2, value=val, anchor=tk.W,
                               font=("Helvetica", 11), padx=10, pady=10)
            if val == 0:
                w.select()
            w.pack(fill=tk.X)

        new_game = tk.Radiobutton(self, text="New game", variable=self.v2, value=(len(games)), anchor=tk.W,
                                  font=("Helvetica", 11), padx=10, pady=10)
        new_game.pack(fill=tk.X)
        okay = tk.Button(self, text="OK", command=lambda: self.callback_game(games, self.v2.get()),
                         font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.choose_server, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

    def show_grid(self, size):
        self.clear()

        title = tk.Label(self, text="Your game name", font=("Helvetica", 16))
        title.grid(row=0, columnspan=2)

        my_grid = tk.Label(self, text="My grid", font=("Helvetica", 12))
        my_grid.grid(row=1, column=0)

        label = tk.Label(self, text="Opponent 1", font=("Helvetica", 12))
        label.grid(row=1, column=1)

        for j in range(2):
            label = tk.Label(self, text="Opponent " + str(j + 2), font=("Helvetica", 12))
            label.grid(row=3, column=j)

        self.my_grid = Grid(self, size, mine=True)
        self.my_grid.grid(row=2, column=0)

        self.my_grid.bind("<1>", self.on_object_click)

        self.opp1_grid = Grid(self, size)
        self.opp1_grid.grid(row=2, column=1)

        self.opp2_grid = Grid(self, size)
        self.opp2_grid.grid(row=3, column=0)
        self.opp3_grid = Grid(self, size)
        self.opp3_grid.grid(row=3, column=1)

        self.center(650, 800)
        # print self.opp2_grid.itemconfig(self.opp2_grid.rect[0, 5], fill="white")

    def on_object_click(self, event):
        print('Got object click', event.x, event.y)
        print(event.widget.find_closest(event.x, event.y))

        for key, value in self.my_grid.rect.iteritems():
            if event.widget.find_closest(event.x, event.y)[0] == value:
                print key, value

    def center(self, width, height):
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def callback_server(self):
        print self.servers[self.v.get()]
        # TODO: siia if-else'id, kui serveriga ei saa yhendust
        self.choose_nickname()

    def callback_nickname(self):
        # TODO: siia if-else'id, kui selline nickname on juba olemas
        print self.nickname.get()
        # TODO: kui nickname'i k2tte saab, siis uus window, kus saab m2ngu valida
        self.choose_game()

    def callback_game(self, games, b):
        if b <= len(games) - 1:
            print "gameeee " + str(games[b])
            # TODO: v6ib kohe serverisse saata, millise m2nguga liituda soovib
            self.show_grid(10)
            # TODO: siin peab serverist saama gridi suuruse
        else:
            print "gameeee New Game"
            choose_grid = tk.Toplevel(self)
            choose_grid.title("Choose the grid size")
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            choose_grid.geometry("250x100+%d+%d" % ((w - 250) / 2, (h - 100) / 2))

            tk.Label(choose_grid, text="Grid size", padx=5, pady=5).pack()

            e = tk.Entry(choose_grid, width=15)
            e.pack(padx=5, pady=5)
            e.focus()

            b = tk.Button(choose_grid, text="OK", command=lambda: self.ok(choose_grid, e))
            b.pack(pady=5, padx=5)

            self.wait_window(choose_grid)

    def ok(self, grid_choose, e):

        print "value is", e.get()
        value = e.get()

        grid_choose.destroy()
        self.show_grid(value)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

    # root = tk.Tk()
    # MainApplication(root).pack(side="top", fill="both", expand=False)
    # win = MainApplication(root)
    # root.mainloop()
