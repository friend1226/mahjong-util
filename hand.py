from typing import Sequence
from enum import Enum

from tile import Tile, Suit


class Meld:
    tiles: tuple[Tile, ...]
    discarded: Tile
    
    def __init__(self, tiles: Sequence[Tile], discarded: Tile):
        self.tiles = tuple(tiles)
        self.discarded = discarded
    
    def is_valid(self) -> bool:
        return False


class Chii(Meld):
    def is_valid(self):
        if len(self.tiles) != 3 or self.discarded not in self.tiles:
            return False
        suits = set(tile.suit for tile in self.tiles)
        if len(suits) > 1:
            return False
        suit = suits.pop()
        if suit == Suit.WIND or suit == Suit.DRAGON:
            return False
        ranks = sorted(tile.rank for tile in self.tiles)
        if ranks[1] - ranks[0] == ranks[2] - ranks[1] == 1:
            return True
        return False


class Pong(Meld):
    def is_valid(self):
        if len(self.tiles) != 3 or self.discarded not in self.tiles:
            return False
        return len(set(self.tiles)) == 1


class KanType(Enum):
    CLOSED = 0
    OPEN = 1
    ADDED_OPEN = 2


class Kan(Meld):
    type_: KanType
    
    def __init__(self, tiles, discarded, type_: KanType):
        super().__init__(tiles, discarded)
        self.type_ = type_
    
    def is_valid(self):
        if len(self.tiles) != 4 or (self.type_ != KanType.CLOSED and self.discarded not in self.tiles):
            return False
        return len(set(self.tiles)) == 1


class Hand:
    hand: list[Tile]
    melds: list[tuple[Tile]]
    
    def __init__(self):
        pass
