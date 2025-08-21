from enum import Enum


class Suit(Enum):
    MAN = 'm'
    PIN = 'p'
    SOU = 's'
    WIND = 'z'
    DRAGON = 'z'


class Tile:
    def __init__(self, rank: int, suit: Suit, red: bool = False):
        self.rank = rank
        self.suit = suit
        self.red = red
    
    def __str__(self):
        return f"{self.rank}{self.suit.value}"

    def __hash__(self):
        return hash((self.rank, self.suit, self.red))

    def __eq__(self, other: 'Tile'):
        return self.rank == other.rank and self.suit == other.suit and self.red == other.red
    
    def equal(self, other: 'Tile'):
        return self.rank == other.rank and self.suit == other.suit

    def dora(self) -> 'Tile':
        next_rank = self.rank + 1

        if self.is_number():
            # 9 -> 1
            if next_rank > 9:
                next_rank = 1
        elif self.is_wind():
            # 북(4) -> 동(1)
            if next_rank > 4:
                next_rank = 1
        elif self.is_dragon():
            # 중(7) -> 백(5)
            if next_rank > 7:
                next_rank = 5

        return Tile(next_rank, self.suit)
    
    def is_number(self) -> bool:
        return self.suit in {Suit.MAN, Suit.PIN, Suit.SOU}
    
    def is_terminal(self) -> bool:
        return self.is_number() and (self.rank == 1 or self.rank == 9)
    
    def is_man(self) -> bool:
        return self.suit == Suit.MAN
    
    def is_pin(self) -> bool:
        return self.suit == Suit.PIN
    
    def is_sou(self) -> bool:
        return self.suit == Suit.SOU

    def is_wind(self) -> bool:
        return self.suit == Suit.WIND
    
    def is_dragon(self) -> bool:
        return self.suit == Suit.DRAGON

    def is_honor(self) -> bool:
        return self.is_wind() or self.is_dragon()
