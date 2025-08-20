from enum import Enum


class Suit(Enum):
    MAN = 'm'
    PIN = 'p'
    SOU = 's'
    WIND = 'z'
    DRAGON = 'z'


class Tile:
    def __init__(self, rank: int, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank}{self.suit.value}"

    def __hash__(self):
        return hash((self.rank, self.suit))

    def __eq__(self, other: 'Tile'):
        return self.rank == other.rank and self.suit == other.suit

    def dora(self) -> 'Tile':
        d_rank, d_suit = self.rank + 1, self.suit
        match self.suit:
            case Suit.MAN | Suit.PIN | Suit.SOU:
                if d_rank > 9:
                    d_rank = 1
            case Suit.WIND:
                if d_rank > 4:
                    d_rank = 1
            case Suit.DRAGON:
                if d_rank > 7:
                    d_rank = 5
        return Tile(d_rank, d_suit)
    
    def is_terminal(self) -> bool:
        return self.suit in {Suit.MAN, Suit.PIN, Suit.SOU} and (self.rank == 1 or self.rank == 9)


class Numbers(Tile):
    red: bool
    
    def __init__(self, rank: int, suit: Suit):
        if rank == 0:
            self.red = True
            rank = 5
        else:
            self.red = False
        super().__init__(rank, suit)


class Honor(Tile):
    pass


class Mansu(Numbers):
    def __init__(self, rank: int):
        super().__init__(rank, Suit.MAN)


class Pinsu(Numbers):
    def __init__(self, rank: int):
        super().__init__(rank, Suit.PIN)


class Sousu(Numbers):
    def __init__(self, rank: int):
        super().__init__(rank, Suit.SOU)


class Wind(Honor):
    pass


class Ton(Wind):
    def __init__(self):
        super().__init__(1, Suit.WIND)


class Nan(Wind):
    def __init__(self):
        super().__init__(2, Suit.WIND)


class Sha(Wind):
    def __init__(self):
        super().__init__(3, Suit.WIND)


class Pei(Wind):
    def __init__(self):
        super().__init__(4, Suit.WIND)


class Dragon(Honor):
    pass


class Haku(Dragon):
    def __init__(self):
        super().__init__(5, Suit.DRAGON)


class Hatsu(Dragon):
    def __init__(self):
        super().__init__(6, Suit.DRAGON)


class Chun(Dragon):
    def __init__(self):
        super().__init__(7, Suit.DRAGON)


East = Ton
South = Nan
West = Sha
North = Pei

White = Haku
Green = Hatsu
Red = Chun
