import Tkinter as tk
from client_comms import query_servers


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # <create the rest of your GUI here>
        self.center(800, 600)
        self.v = tk.IntVar()
        self.nickname = tk.Entry(self, width=30)

        self.servers = query_servers()
        self.choose_server()

    def choose_server(self):
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

        # nickname_label = tk.Label(self, text="Choose your nickname:", anchor=tk.W, font=("Helvetica", 12),
        #                           padx=15, pady=10)
        # nickname_label.pack(fill=tk.X)
        # self.nickname.pack(anchor=tk.W, padx=15, pady=10)
        # # entry.bind('<Return>', showentry) # if you press enter, the entered text is printed out

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

        okay = tk.Button(self, text="OK", command=self.callback_nickname, font=("Helvetica", 12), padx=15, pady=10)
        okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
        cancel = tk.Button(self, text="Cancel", command=self.destroy, font=("Helvetica", 12),
                           padx=15, pady=10)
        cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

    def center(self, width, height):
        x = (self.winfo_screenwidth() / 2) - (width / 2)
        y = (self.winfo_screenheight() / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def callback_server(self):
        print self.servers[self.v.get()]
        #TODO: siia if-else'id, kui serveriga ei saa yhendust
        self.choose_nickname()

    def callback_nickname(self):
        #TODO: siia if-else'id, kui selline nickname on juba olemas
        print self.nickname.get()
        #TODO: kui nickname'i kätte saab, siis uus window



if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

    #root = tk.Tk()
    #MainApplication(root).pack(side="top", fill="both", expand=False)
    #win = MainApplication(root)
    #root.mainloop()
