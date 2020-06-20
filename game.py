from cards import Cards
from player import Player, AI
from socketserver import ThreadingTCPServer
from socketserver import BaseRequestHandler
from protocol import Protocol, dbg
from threading import Thread, Lock
from time import sleep

lock = Lock() # 同时只能有一个线程操作g

class Game:

    def __init__(self):
        self.cards = Cards()
        self.playerCounter = 0
        self.player = [None, None, None, None]
        self.started = 0
        self.finish = 0

    def start(self) -> bool:
        with lock:
            if not self.started and self.playerCounter == 4:
                self.started = 1
            else:
                return
        
            if dbg: print("game start")

            self.cards.shuffle()
            deal = self.cards.deal()
            for i in range(0,4):
                self.player[i].getCards(deal[i])
                print("player", i, deal[i])

            # UTF-8编码，0-127都是单字节
            t = Thread(target = self.player[0].play(3,[127,127,127,127,127]))
            t.start()

    def addPlayer(self, Player, socket = None) -> bool:
        with lock:
            ind = -1
            for i, p in enumerate(self.player):
                if p == None:
                    ind = i
                    break
            if ind == -1: return -1, None
            
            for p in self.player:
                if p != None:
                    p.addPlayer(ind)
            self.playerCounter += 1
            self.player[ind] = Player(socket, ind, self)

            if dbg:
                print("addPlayer", ind)
                print("now player", self.player)

            return ind, self.player
        
    def delPlayer(self, ind: int):
        with lock:
            if g.started and type(self.player[ind]) == AI: return
            g.started = 0
            self.player[ind] = None

            for p in self.player:
                if p != None:
                    p.delPlayer(ind)
            self.playerCounter -= 1

            # 无玩家清场功能
            clr_flg = 1
            for p in self.player:
                if type(p) == Player: clr_flg = 0
            if clr_flg:
                self.player = [None, None, None, None]
                self.playerCounter = 0

            if dbg:
                print("delPlayer", ind)
                print("now player", self.player)
    

class ServerSocket(BaseRequestHandler):

    def setup(self):
        self.ind = -1
        print("连接建立：",self.client_address)
    def finish(self):
        if self.ind != -1: g.delPlayer(self.ind)
        print("连接终止: ",self.client_address)
    def handle(self):
        while 1:
            try:

                s = self.request.recv(1024).decode('UTF-8')[2:]
                if not s: break
                print(self.client_address, s.encode())

                if s[0] == Protocol.加入游戏:

                    ret = g.addPlayer(Player, self)
                    if ret[0] == -1:
                        self.request.sendall(Protocol.房间已满.encode())
                    else:
                        self.ind = ret[0]
                        data = Protocol.加入游戏 + chr(ret[0])
                        for p in ret[1]: data += (chr(0) if p == None else chr(1))
                        self.request.sendall(data.encode())

                elif s[0] == Protocol.添加电脑:
                    g.addPlayer(AI, None)
                        
                elif s[0] == Protocol.退出游戏:
                    g.delPlayer(int(s[1]))

                elif s[0] == Protocol.删除电脑:
                    for i, p in enumerate(reversed(g.player)):
                        if isinstance(p,AI):
                            g.delPlayer(3-i)
                            break

                if not g.started:
                    g.start()

            except Exception as e:
                print(e)
                break


if __name__ == "__main__":
    g = Game()
    host, port = '127.0.0.1', 5000
    server = ThreadingTCPServer((host,port),ServerSocket)
    print("初始化完毕，等待连接")
    server.serve_forever()

