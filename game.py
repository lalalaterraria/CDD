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
        self.now_player = 0
        self.pass_cnt = 0
        self.pre_cards = []

    def game_over(self, ind):
        with lock:
            print("winner", ind)

    def next_player(self, now_cards: list):
        with lock:
            ok = self.cards.check(self.pre_cards, now_cards)
            if(dbg): print("player/AI", self.now_player, "display", now_cards, ("ok" if ok else "not ok"))
            if not ok:
                t = Thread(target = self.player[self.now_player].play, args = ((len(self.pre_cards) != 0) | 2,))
                t.start()
            else:

                if dbg:
                    for i in range(0,4):
                        print("player", i, self.player[i].card)
                    print("---------------------------------------------")
                    print()
                    print("---------------------------------------------")

                for p in self.player: p.display(self.now_player, now_cards)
                if len(now_cards) == 0:
                    self.pass_cnt += 1
                    # 三人pass，则大者继续出牌
                    if self.pass_cnt == 3: self.pass_cnt, self.pre_cards = 0, []
                else:
                    self.pass_cnt = 0
                    self.pre_cards = now_cards
                
                self.now_player = (self.now_player + 1) % 4
                t = Thread(target = self.player[self.now_player].play, args = (len(self.pre_cards) != 0,))
                t.start()

    def start(self):
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
                if dbg: print("player", i, deal[i])

            self.now_player = 0            
            self.pass_cnt = 0
            self.pre_cards = []
            self.player[0].play(0)

    def addPlayer(self, Player, socket = None):
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

                r = self.request.recv(1024)
                print("recv", self.client_address, r)

                s = r.decode('UTF-8')[2:]
                if not s: break

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

                elif s[0] == Protocol.开始出牌:
                    # 安卓标准库内鬼ascll0编码为\xc0\x80
                    # 所以将0临时编码为52，这里转换回来
                    cards = [ord(i)%52 for i in s][1:]
                    g.next_player(cards)

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

