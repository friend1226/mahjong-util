from dataclasses import dataclass
from collections import deque
from random import shuffle
from enum import Enum, auto
from typing import Optional

from .tile import Tile, Suit


class GameMode(Enum):
    SAMA = FOUR_BASIC = DEFAULT = auto()
    SAMMA = THREE_BASIC = auto()


@dataclass()
class PlayerState:
    riichi: bool


class GameState:
    wall: deque[Tile]
    # 영상패 | 도라표시패 | 패
    linshang: list[Tile]
    dora: list[Tile]
    ura_dora: list[Tile]
    dora_opened: int
    linshang_drawn: int
    
    players: list[PlayerState]
    
    def __init__(self, players: list[PlayerState], mode=GameMode.DEFAULT):
        self.mode = mode
        match self.mode:
            case GameMode.SAMA:
                tiles = [Tile(i, suit) for suit in Suit for i in range(1, 10)][:-2] * 4
                shuffle(tiles)
                self.wall = deque(tiles)
                self.linshang = []
                self.dora = []
                self.ura_dora = []
                for _ in range(4):
                    self.linshang.append(self.wall.popleft())
                for _ in range(5):
                    self.dora.append(self.wall.popleft())
                    self.ura_dora.append(self.wall.popleft())
            case _:
                self.wall = []
                self.linshang = []
                self.dora = []
                self.ura_dora = []
        self.dora_opened = 1
        self.linshang_drawn = 0
        self.players = players
    
    def tsumo(self) -> Optional[Tile]:
        if len(self.wall) <= self.linshang_drawn:
            return None
        return self.wall.pop()
    
    def tsumo_linshang(self) -> Optional[Tile]:
        if self.dora_opened >= 5:
            return None
        self.linshang_drawn += 1
        return self.linshang[self.linshang_drawn - 1]
    
    def open_dora(self) -> bool:
        if self.dora_opened >= 5:
            return False
        self.dora_opened += 1
        return True