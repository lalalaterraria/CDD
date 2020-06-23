from protocol import Protocol, dbg
from threading import Thread

class Player:

    def __init__(self, socket, ind, g):
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

    def game_over(self, ind):
        self.socket.request.sendall((Protocol.游戏结束 + chr(ind)).encode())

    def addPlayer(self, ind: int):
        self.socket.request.sendall((Protocol.玩家加入 + chr(ind)).encode())

    def delPlayer(self, ind: int):
        self.socket.request.sendall((Protocol.玩家退出 + chr(ind)).encode())

    def play(self, flg: int):
        '''flg: flg&1=0,强制出牌,否则不强制出牌,
                flg&2=0,上次出牌合法，否则上次出牌不合法
        '''

        # if(len(self.card) == 0):
        #     t = Thread(target = self.g.game_over,args = (self.ind,))
        #     t.start()
        #     return

        if dbg: print("turn to player", self.ind, "play")
        self.socket.request.sendall((Protocol.开始出牌 + chr(flg)).encode())

    # 返回值表示这轮是否出完
    def display(self, ind: int, cards: list):
        # 自己成功出牌需要扣除
        if ind == self.ind: self.card = list(set(self.card) - set(cards))

        data = Protocol.成功出牌 + chr(ind)
        for i in cards:
            data += chr(i)
        while len(data) != 7: data = data[:2] + chr(127) + data[2:]
        self.socket.request.sendall(data.encode())

        if len(self.card) == 0: return 1
        else: return 0

# AI不需要通知客户端，也没有UI，比较简单
from random import randint
from time import sleep
class AI(Player):

    def __init__(self, socket, ind, g):
        super().__init__(socket, ind, g)
        self.pre_cards = []

    def getCards(self, cards: list):
        self.card = cards

    def addPlayer(self, ind: int):
        pass

    def delPlayer(self, ind: int):
        pass

    def play(self, flg: int):
        '''flg: flg=0,强制出牌,否则不强制出牌
        '''

        sleep(0.6)

        if(len(self.card) == 0):
            t = Thread(target = self.g.game_over,args = (self.ind,))
            t.start()
            return

        if dbg: print("turn to AI", self.ind, "play")

        # 20%概率直接pass
        # if flg == 1 and randint(0,4) == 0:
        #     t = Thread(target = self.g.next_player,args = ([],))
        #     t.start()

        def now_cards(now_ind: list):
            return [self.card[i] for i in now_ind]

         # 爆枚找到一个合法解，至多枚举1287次
        def dfs(dep, lim, now_ind: list):
            # print("enumerate", dep, now_ind, now_cards(now_ind))
            if dep == lim:
                if self.g.cards.check(self.pre_cards, now_cards(now_ind)):
                    self.flg = 1
                return
            s = -1 if len(now_ind) == 0 else now_ind[dep-1]
            for now in range(s+1,self_len):
                now_ind.append(now)
                dfs(dep+1, lim, now_ind)
                if self.flg == 1: return
                now_ind.pop()

        now_ind = []
        pre_len = len(self.pre_cards)
        self_len = len(self.card)

        if(pre_len == 0):
            if self.g.game_args[2] == 0:
                tmp = min(self_len,5)
                for i in range(tmp,0,-1):
                    self.flg = 0
                    dfs(0, i, now_ind)
                    if len(now_ind): break
            else: now_ind = [0]

        elif pre_len > self_len:
            now_ind = []

        else:
            self.flg = 0
            dfs(0, pre_len, now_ind)

        t = Thread(target = self.g.next_player,args = (now_cards(now_ind),))
        t.start()

    def display(self, ind: int, cards: list):

        # print("AI display", ind, cards)

        if ind == self.ind:
            self.card = list(set(self.card) - set(cards))
            self.pre_cards = []
        elif len(cards) != 0: self.pre_cards = cards

        # print("AI pre_cards", ind, self.pre_cards)

        if len(self.card) == 0: return 1
        else: return 0
