import random
import protocol

class TYPE:
    UNKNOWN    = 0
    ONE        = 1
    TWO        = 2
    THREE      = 3
    STRAIGHT   = 4
    SUITFIVE   = 5
    THREE_TWO  = 6
    FOUR_ONE   = 7
    FLASH      = 8

    point      = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    suit       = ['方块','梅花','红桃','黑桃']
    name       = ['未知','单张','两张','三张','顺子','同花五','三带二','四带一','同花顺']

class Cards:

    def __init__(self):
        self.card = [i for i in range(0,52)]

    def shuffle(self) -> None:
        random.shuffle(self.card)

    def deal(self):
        '''retutn: cards[4]
        '''
        ret = []
        for i in range(0,4):
            tmp = self.card[i*13:(i+1)*13]
            def suit(x: int): return x//13
            def point(x: int): return x%13
            tmp.sort(key = lambda x: (point(x),suit(x)))
            ret.append(tmp)
        return ret

    def checkType(self, cards: list):
        '''return: TYPE, maxCard
        '''

        def suit(x: int):
            return x//13

        def point(x: int):
            return x%13

        def card(x: int):
            return x[0] + x[1]*13

        def same(x: list) -> bool:
            for i in x:
                if i != x[0]:
                    return 0
            return 1

        def straight(_cards: list):
            '''return: TYPE, maxCard
            '''
            p = list(map(point, _cards))
            s = list(map(suit, _cards))
            if p[-1] == 12:
                p[-1] = -1
                s.pop()
                p.sort()

            if p[-1] == 11 and p[-2] != 10:
                p[-1] = -2
                s.pop()
                p.sort()

            for i, j in enumerate(p):
                if i != j - p[0]:
                    return 0, 0
            return 1, card((p[-1],s[-1]))

        cards.sort(key = lambda x: (point(x),suit(x)))

        if len(cards) == 1: 
            return TYPE.ONE, cards[0]

        if len(cards) == 2:
            if same(list(map(point, cards))):
                return TYPE.TWO, cards[0]
            else:
                return TYPE.UNKNOWN, -1
            
        if len(cards) == 3:
            if same(list(map(point, cards))):
                return TYPE.THREE, cards[0]
            else:
                return TYPE.UNKNOWN, -1
            
        if len(cards) == 4:
            return TYPE.UNKNOWN, -1

        if len(cards) == 5:
            if same(list(map(point, cards[:-1]))):
                return TYPE.FOUR_ONE, cards[-2]
            if same(list(map(point, cards[1:]))):
                return TYPE.FOUR_ONE, cards[-1]
            
            if same(list(map(point, cards[:-2]))) and same(list(map(point, cards[-2:]))):
                return TYPE.THREE_TWO, cards[-3]
            if same(list(map(point, cards[:2]))) and same(list(map(point, cards[2:]))):
                return TYPE.THREE_TWO, cards[-1]

            straightFlg, maxCard = straight(cards)
            suitfiveFlg = same(list(map(suit, cards)))

            if straightFlg and suitfiveFlg:
                return TYPE.FLASH, maxCard 
            if not straightFlg and suitfiveFlg:
                return TYPE.SUITFIVE, cards[-1]
            if straightFlg and not suitfiveFlg:
                return TYPE.STRAIGHT, maxCard
            return TYPE.UNKNOWN, -1
        
        if len(cards) >=6:
            return TYPE.UNKNOWN, -1

    def check(self, pre_cards: list, now_cards: list) -> bool:
        pre_type, pre_mc = self.checkType(pre_cards)
        now_type, now_mc = self.checkType(now_cards)
        if len(pre_cards) != len(now_cards) or now_type == TYPE.UNKNOWN: return 0
        def suit(x: int): return x//13
        def point(x: int): return x%13
        return pre_type < now_type or pre_type == now_type \
            and (point(pre_mc) < point(now_mc) or point(pre_mc) == point(now_mc) and suit(pre_mc)< suit(now_mc))

if __name__ == "__main__":
    while 1:
        n = int(input("total cards number:"))
        c = Cards()
        cards = []

        def suit(x): return x//13
        def point(x): return x%13
        def card(x): return x[0] + x[1]*13

        print("point(0-12) suit(0-3):")
        for i in range(n):
            p, s = map(int, input().strip().split())
            cards.append(card((p,s)))
        ans = c.checkType(cards)

        print("cards:", [(TYPE.point[point(i)],TYPE.suit[suit(i)]) for i in cards])
        print("checked TYPE:", TYPE.name[ans[0]])
        print("maxCard:", (TYPE.point[point(ans[1])], TYPE.suit[suit(ans[1])]))