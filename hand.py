from typing import Sequence as Seq, Iterable, Optional
from enum import Enum
from itertools import product, combinations, chain

from tile import Tile, Suit


class TileGroup:
    tiles: tuple[Tile, ...]
    discarded: Tile
    called: int
    
    def __init__(self, tiles: Seq[Tile], discarded: Tile, called: int):
        self.tiles = tuple(sorted(tiles))
        self.discarded = discarded
        self.called = called
        # 0 = not called
        # 1 = from left player
        # 2 = from opposite player
        # 3 = from right player
    
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
    
    def call_acceptable_list(self, tile: Tile) -> list[tuple[CallType, Seq[Tile]]]:
        result_list = []
        hand_group = {suit: [[] for _ in range(10)] for suit in Suit}
        for hand_tile in self.hand:
            hand_group[hand_tile.suit][hand_tile.rank].append(hand_tile)
        if tile.is_number():
            if tile.rank >= 3:
                for t1, t2 in product(set(hand_group[tile.suit][tile.rank - 2]), set(hand_group[tile.suit][tile.rank - 1])):
                    result_list.append((CallType.CHII, [t1, t2]))
            if 2 <= tile.rank <= 8:
                for t1, t2 in product(set(hand_group[tile.suit][tile.rank + 1]), set(hand_group[tile.suit][tile.rank - 1])):
                    result_list.append((CallType.CHII, [t1, t2]))
            if tile.rank <= 7:
                for t1, t2 in product(set(hand_group[tile.suit][tile.rank + 1]), set(hand_group[tile.suit][tile.rank + 2])):
                    result_list.append((CallType.CHII, [t1, t2]))
        for tiles in set(combinations(hand_group[tile.suit][tile.rank], 2)):  # No iteration if less than 2
            result_list.append((CallType.PON, tiles))
        for tiles in set(combinations(hand_group[tile.suit][tile.rank], 3)):  # No iteration if less than 3
            result_list.append((CallType.KAN_OPEN, tiles))
        for meld in self.melds:
            if isinstance(meld, Triplet) and meld.discarded.equal(tile):
                result_list.append((CallType.KAN_ADDED_OPEN, [tile]))
        return result_list
    
    def call(self, call_type: CallType, tile: Optional[Tile], matching_tiles: Iterable[Tile], called_from: int) -> bool:
        hand_group = {suit: [[] for _ in range(10)] for suit in Suit}
        for hand_tile in self.hand:
            hand_group[hand_tile.suit][hand_tile.rank].append(hand_tile)
        match call_type:
            case CallType.KAN_CLOSED:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Quad(matching_tiles, tile, called_from, QuadType.CLOSED))
            case CallType.KAN_ADDED_OPEN:
                try:
                    hand_group[tile.suit][tile.rank].remove(tile)
                except ValueError:
                    return False
                for (idx, meld) in enumerate(self.melds):
                    if isinstance(meld, Triplet) and meld.called > 0 and meld.tiles == tuple(sorted(matching_tiles)):
                        break
                else:
                    return False
                self.melds.remove(meld)
                self.melds.insert(idx, Quad(matching_tiles, tile, called_from, QuadType.ADDED_OPEN))
            case CallType.CHII:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Sequence(matching_tiles, tile, called_from))
            case CallType.PON:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Triplet(matching_tiles, tile, called_from))
            case CallType.KAN_OPEN:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Quad(matching_tiles, tile, called_from, QuadType.OPEN))
        self.hand = [*chain(*chain(*hand_group.values()))]
        return True
