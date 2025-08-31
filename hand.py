from typing import Sequence as Seq, Iterable, Optional
from enum import Enum
from itertools import product, combinations, chain
from collections import deque

from tile import Tile, CalledTile, Suit


class TileGroup:
    tiles: tuple[Tile, ...]
    called: Optional[CalledTile]
    
    def __init__(self, tiles: Seq[Tile], called: Optional[CalledTile] = None):
        self.tiles = tuple(sorted(tiles))
        self.called = called
    
    def __repr__(self):
        if self.called is None:
            return f"{self.__class__.__name__}({''.join(map(str, self.tiles))})"
        else:
            rest_of_tiles = list(self.tiles)
            rest_of_tiles.remove(self.called.tile)
            match self.called.from_:
                case 1:
                    return f"{self.__class__.__name__}({self.called.tile}-{''.join(map(str, rest_of_tiles))}"
                case 2:
                    half_index = len(rest_of_tiles)//2
                    return f"{self.__class__.__name__}({''.join(map(str, rest_of_tiles[:half_index]))}-" \
                           f"{self.called.tile}-{''.join(map(str, rest_of_tiles[half_index:]))}"
                case 3:
                    return f"{self.__class__.__name__}({''.join(map(str, rest_of_tiles))}-{self.called.tile})"
                case _:
                    return f"{self.__class__.__name__}({''.join(map(str, self.tiles))})"
    
    def __hash__(self):
        return hash((self.tiles, self.called))
    
    def is_valid(self) -> bool:
        return self.called is None or self.called.tile in self.tiles
    
    @classmethod
    def fromTileGroup(cls, tile_group: 'TileGroup'):
        return cls(tile_group.tiles, tile_group.called)


class Head(TileGroup):
    def is_valid(self) -> bool:
        return self.called is None and len(self.tiles) == 2 and self.tiles[0].is_same(self.tiles[1])


class Sequence(TileGroup):
    def is_valid(self):
        if len(self.tiles) != 3 or not super().is_valid():
            return False
        suits = set(tile.suit for tile in self.tiles)
        if len(suits) > 1:
            return False
        suit = suits.pop()
        if suit == Suit.WIND or suit == Suit.DRAGON:
            return False
        ranks = sorted(tile.rank for tile in self.tiles)
        return ranks[1] - ranks[0] == ranks[2] - ranks[1] == 1


class Triplet(TileGroup):
    def is_valid(self):
        if len(self.tiles) != 3 or not super().is_valid():
            return False
        return len(set(self.tiles)) == 1


class QuadType(Enum):
    CLOSED = 0
    OPEN = 1
    ADDED_OPEN = 2


class Quad(TileGroup):
    type_: QuadType
    
    def __init__(self, tiles: Seq[Tile], type_: QuadType, called: Optional[CalledTile] = None):
        super().__init__(tiles, called)
        self.type_ = type_
    
    def is_valid(self):
        if len(self.tiles) != 4 or (self.type_ != QuadType.CLOSED and not super().is_valid()):
            return False
        return len(set(self.tiles)) == 1


Mentsu = TileGroup
Toitsu = Head
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
    
    def __repr__(self):
        if self.melds:
            return f"Hand({''.join(map(str, self.hand))},{''.join(map(str, self.melds))})"
        else:
            return f"Hand({''.join(map(str, self.hand))})"
    
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
            if isinstance(meld, Triplet) and meld.called.tile.is_same(tile):
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
                self.melds.append(Quad(matching_tiles, QuadType.CLOSED, None))
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
                self.melds.insert(idx, Quad(matching_tiles, QuadType.ADDED_OPEN, meld.called))
            case CallType.CHII:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Sequence(matching_tiles, CalledTile(tile, called_from)))
            case CallType.PON:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Triplet(matching_tiles, CalledTile(tile, called_from)))
            case CallType.KAN_OPEN:
                try:
                    for t in matching_tiles:
                        hand_group[t.suit][t.rank].remove(t)
                except ValueError:
                    return False
                self.melds.append(Quad(matching_tiles, QuadType.OPEN, CalledTile(tile, called_from)))
        self.hand = [*chain(*chain(*hand_group.values()))]
        return True
    
    def parse(self) -> list[list[TileGroup]]:
        result = []
        parse_queue: deque[tuple[int, list[Tile], list[TileGroup], list[TileGroup]]] = deque([(0, [], [], [])])
        # index, 1-length, 2-length, 3-length
        hand_ordered = sorted(self.hand)
        while parse_queue:
            tile_idx, *parsed = parse_queue.popleft()
            if tile_idx == len(hand_ordered):
                result.append([*self.melds, *chain.from_iterable(parsed)])
                continue
            tile = hand_ordered[tile_idx]
            parse_queue.append((tile_idx + 1, [*parsed[0], tile], parsed[1], parsed[2]))
            if parsed[0]:
                p_tile = parsed[0][-1]
                if tile.suit == p_tile.suit:
                    if tile.rank - p_tile.rank == 1:
                        parse_queue.append((tile_idx + 1, parsed[0][:-1], [*parsed[1], Sequence([parsed[0][-1], tile])], parsed[2]))
                    elif tile.rank == p_tile.rank:
                        parse_queue.append((tile_idx + 1, parsed[0][:-1], [*parsed[1], Head([parsed[0][-1], tile])], parsed[2]))
            if parsed[1]:
                match parsed[1][-1]:
                    case Head(tiles=tiles):
                        if tile.is_same(tiles[0]):
                            parse_queue.append((tile_idx + 1, parsed[0], parsed[1][:-1], [*parsed[2], Triplet([*tiles, tile])]))
                    case Sequence(tiles=tiles):
                        if tile.suit == tiles[0].suit and tile.rank == tiles[1].rank + 1:
                            parse_queue.append((tile_idx + 1, parsed[0], parsed[1][:-1], [*parsed[2], Sequence([*tiles, tile])]))
        result.sort(key=lambda x: len(x))
        return result


if __name__ == '__main__':
    hand = Hand()
    hand.add_tiles(map(Tile.from_str, "2m 2m 2m 3m 3m 3m 4m 4m 4m".split()))
    print(hand)
    hand_parse = hand.parse()
    print(*hand_parse, sep='\n')
