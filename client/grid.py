import Tkinter as tk

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
            self.grid_size = int(size) * 28 + 10
        self.rows = int(size)
        self.columns = int(size)
        self.cellheight = 25
        self.cellwidth = 25
        self.rect = {}
        self.config(height=self.grid_size, width=self.grid_size)
        self.mine = mine
        self.player = ""
        self.shots = []
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

                if self.mine:
                    self.itemconfig(self.rect[row, column], tags=self)

    def clear_grid(self):
        for column in range(self.columns):
            for row in range(self.rows):
                self.rect[row, column].configure(fill="")


class GridFrame(tk.Frame):
    def __init__(self, master, size, mine):
        tk.Frame.__init__(self, master=master)

        self.master = master
        self.gridp = Grid(self, size, mine=mine)

        if mine:
            self.label = tk.Label(self, text="My grid", font=("Helvetica", 12))
        else:
            self.label = tk.Label(self, text="Opponent", font=("Helvetica", 12))

        self.label.grid(row=0, column=0)
        self.gridp.grid(row=1, column=0)
