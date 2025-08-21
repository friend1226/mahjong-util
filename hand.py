from typing import Sequence, Iterable
from enum import Enum
from collections import Counter

from tile import Tile, Suit


class TileGroup:
    tiles: tuple[Tile, ...]
    discarded: Tile
    called: bool
    
    def __init__(self, tiles: Sequence[Tile], discarded: Tile, called: bool):
        self.tiles = tuple(tiles)
        self.discarded = discarded
        self.called = called
    
    def is_valid(self) -> bool:
        return self.discarded in self.tiles


class Sequence(TileGroup):
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
        return super().is_valid()


class Triplet(TileGroup):
    def is_valid(self):
        if len(self.tiles) != 3 or self.discarded not in self.tiles:
            return False
        return len(set(self.tiles)) == 1 and super().is_valid()


class QuadType(Enum):
    CLOSED = 0
    OPEN = 1
    ADDED_OPEN = 2


class Quad(TileGroup):
    type_: QuadType
    
    def __init__(self, tiles, discarded, called, type_: QuadType):
        super().__init__(tiles, discarded, called)
        self.type_ = type_
    
    def is_valid(self):
        if len(self.tiles) != 4 or (self.type_ != QuadType.CLOSED and self.discarded not in self.tiles):
            return False
        return len(set(self.tiles)) == 1


Mentsu = TileGroup
Shuntsu = Sequence
Kotsu = Triplet
Kantsu = Quad


class CallType(Enum):
    CHII = 1
    PON = 2
    KAN_CLOSED = 3
    KAN_OPEN = 4
    KAN_ADDED_OPEN = 5


class Hand:
    hand: list[Tile]
    melds: list[TileGroup]
    
    def __init__(self):
        self.hand = []
        self.melds = []
    
    def add_tile(self, tile: Tile):
        self.hand.append(tile)
    
    def add_tiles(self, tiles: Iterable[Tile]):
        self.hand.extend(tiles)
    
    def call_acceptable_list(self, tile: Tile) -> list[tuple[CallType, TileGroup]]:
        result_list = []
        hand_table = {suit: [0]*10 for suit in Suit}
        for hand_tile in self.hand:
            hand_table[hand_tile.suit][hand_tile.rank] += 1
        if tile.is_number():
            if tile.rank >= 3 and hand_table[tile.suit][tile.rank - 2] >= 1 and hand_table[tile.suit][tile.rank - 1] >= 1:
                result_list.append((
                    CallType.CHII, 
                    Shuntsu([Tile(tile.rank - 2, tile.suit), Tile(tile.rank - 1, tile.suit), tile], tile, False)
                    ))
            if tile.rank <= 7 and hand_table[tile.suit][tile.rank + 1] >= 1 and hand_table[tile.suit][tile.rank + 2] >= 1:
                result_list.append((
                    CallType.CHII, 
                    Shuntsu([Tile(tile.rank + 1, tile.suit), Tile(tile.rank + 2, tile.suit), tile], tile, False)
                    ))
        if hand_table[tile.suit][tile.rank] >= 3:
            result_list.append((CallType.PON, Triplet([tile]*3, tile, False)))
        if hand_table[tile.suit][tile.rank] >= 4:
            result_list.append((CallType.KAN_OPEN, Quad([tile]*4, tile, False, QuadType.CLOSED)))
        for meld in self.melds:
            if isinstance(meld, Triplet) and meld.discarded.equal(tile):
                result_list.append((CallType.KAN_ADDED_OPEN, Quad(meld.tiles, tile, False, QuadType.ADDED_OPEN)))

