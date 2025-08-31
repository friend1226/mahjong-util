from enum import Enum, nonmember
from dataclasses import dataclass


class Suit(Enum):
    MAN = 'm'
    PIN = 'p'
    SOU = 's'
    WIND = 'z'
    DRAGON = 'z'
    order = nonmember({MAN: 0, PIN: 1, SOU: 2, WIND: 3, DRAGON: 4})
    
    def __lt__(self, other: 'Suit'):
        return Suit.order[self.value] < Suit.order[other.value]
    
    def __le__(self, other: 'Suit'):
        return Suit.order[self.value] <= Suit.order[other.value]

    def __gt__(self, other: 'Suit'):
        return Suit.order[self.value] > Suit.order[other.value]

    def __ge__(self, other: 'Suit'):
        return Suit.order[self.value] >= Suit.order[other.value]

@dataclass(frozen=True)
class Tile:
    rank: int
    suit: Suit
    red: bool = False
    
    def __str__(self):
        return f"{self.rank}{self.suit.value}"

    def __repr__(self):
        return f"Tile({self.rank}{self.suit.value})"

    def __hash__(self):
        return hash((self.rank, self.suit, self.red))

    def __eq__(self, other: 'Tile'):
        return self.rank == other.rank and self.suit == other.suit and self.red == other.red
    
    def __lt__(self, other: 'Tile'):
        if self.suit == other.suit:
            return self.rank < other.rank
        return self.suit < other.suit
    
    def __le__(self, other: 'Tile'):
        if self.suit == other.suit:
            return self.rank <= other.rank
        return self.suit <= other.suit

    def __gt__(self, other: 'Tile'):
        if self.suit == other.suit:
            return self.rank > other.rank
        return self.suit > other.suit

    def __ge__(self, other: 'Tile'):
        if self.suit == other.suit:
            return self.rank >= other.rank
        return self.suit >= other.suit
    
    def is_same(self, other: 'Tile'):
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
    
    @classmethod
    def from_str(cls, s: str) -> 'Tile':
        rank = int(s[:-1])
        if s[-1] == 'z':
            if rank > 4:
                return Tile(rank, Suit.DRAGON)
            return Tile(rank, Suit.WIND)
        return Tile(rank, Suit(s[-1]))
    
    def is_number(self) -> bool:
        return self.suit.value != 'z'
    
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


@dataclass
class CalledTile:
    tile: Tile
    from_: int
    # 0 = not called
    # 1 = from left player
    # 2 = from opposite player
    # 3 = from right player
