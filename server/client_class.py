class Client:
    def __init__(self, ip, port, socket, nick="default"):
        self.nick = nick
        self.ip = ip
        self.port = port
        self.socket = socket

    def update_nick(self, new_nick):
        if len(new_nick) < 3 or len(new_nick) > 29:
            return False
        else:
            self.nick = new_nick
            return True

    def __repr__(self):
        return self.nick + " " + str(self.ip) + " " + str(self.port) + " " + str(self.socket)
