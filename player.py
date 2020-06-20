from protocol import Protocol, dbg

class Player:

    def __init__(self, socket, ind: int, g):
        if dbg: print("new palyer", ind)
        self.card = []
        self.socket = socket
        self.ind = ind
        self.g = g

    def getCards(self, cards: list):
        self.card = cards
        data = Protocol.游戏开始
        for i in cards:
            data += chr(i)
        self.socket.request.sendall(data.encode())
        # print(data.encode())

    def addPlayer(self, ind: int):
        self.socket.request.sendall((Protocol.玩家加入 + chr(ind)).encode())

    def delPlayer(self, ind: int):
        self.socket.request.sendall((Protocol.玩家退出 + chr(ind)).encode())

    def play(self, pass_cnt: int, pre_cards: list):
        data = Protocol.开始出牌 + chr(pass_cnt)
        for i in pre_cards:
            data += chr(i)
        self.socket.request.sendall(data.encode())
        # print(data.encode())

class AI(Player):

    def getCards(self, cards: list):
        pass

    def addPlayer(self, ind: int):
        pass

    def delPlayer(self, ind: int):
        pass

    def play(self):
        pass
