class Client:
    def __init__(self, ip, port, socket, nick="default"):
        self.nick = nick
        self.ip = ip
        self.port = port
        self.socket = socket

    def update_nick(self, new_nick):
        self.nick = new_nick
