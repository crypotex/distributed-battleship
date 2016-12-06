import Tkinter as tk

def center(width, height):
    x = (root.winfo_screenwidth() / 2) - (width / 2)
    y = (root.winfo_screenheight() / 2) - (height / 2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def callback():
    print "clicked OK! " + str(v.get()) + ", nickname: " + str(nickname.get())

root = tk.Tk()

w = 800  # width for the Tk root
h = 650  # height for the Tk root
center(w, h)

title = tk.Label(root, text="Game servers", font=("Helvetica", 16))
title.pack(side=tk.TOP, fill=tk.X)

label = tk.Label(root, text="Choose a server to connect to:", anchor=tk.W, font=("Helvetica", 12), padx=15, pady=10)
label.pack(fill=tk.X)

servers = ["yks", "kaks"]
v = tk.IntVar()
for val, server in enumerate(servers):
    w = tk.Radiobutton(root, text=server, variable=v, value=val, anchor=tk.W,
                       font=("Helvetica", 11), padx=10, pady=10)
    if val == 0:
        w.select()
    w.pack(fill=tk.X)


nickname_label = tk.Label(root, text="Choose your nickname:", anchor=tk.W, font=("Helvetica", 12), padx=15, pady=10)
nickname = tk.Entry(root, width=30)
nickname_label.pack(fill=tk.X)
nickname.pack(anchor=tk.W, padx=15, pady=10)
#entry.bind('<Return>', showentry) # if you press enter, the entered text is printed out


okay = tk.Button(root, text="OK", command=callback, font=("Helvetica", 12), padx=15, pady=10)
okay.pack(anchor=tk.SE, side=tk.RIGHT, padx=15, pady=15)
cancel = tk.Button(root, text="Cancel", command=root.destroy, font=("Helvetica", 12), padx=15, pady=10)
cancel.pack(anchor=tk.SE, side=tk.RIGHT, padx=5, pady=15)

#entry.pack()
root.mainloop()
