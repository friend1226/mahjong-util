import unittest
from tile import (
    Suit, Tile, Numbers, Honor,
    Mansu, Pinsu, Sousu,
    Wind, Ton, Nan, Sha, Pei,
    Dragon, Haku, Hatsu, Chun,
    East, South, West, North,
    White, Green, Red
)

class TestTileFunctionality(unittest.TestCase):
    """Tests for Mahjong tile classes."""

    def test_base_tile(self):
        """Tests the base Tile class functionality."""
        t1 = Tile(1, Suit.MAN)
        t2 = Tile(1, Suit.MAN)
        t3 = Tile(2, Suit.MAN)
        t4 = Tile(1, Suit.PIN)

        # Test equality
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)
        self.assertNotEqual(t1, t4)

        # Test string representation
        self.assertEqual(str(t1), "1m")
        self.assertEqual(str(t4), "1p")

        # Test hashability
        s = {t1, t2, t3, t4}
        self.assertEqual(len(s), 3)
        self.assertIn(t1, s)
        self.assertIn(t2, s) # t2 is same as t1
        self.assertIn(t3, s)
        self.assertIn(t4, s)

    def test_numbered_tiles(self):
        """Tests Mansu, Pinsu, and Sousu tiles."""
        m1 = Mansu(1)
        self.assertEqual(m1.rank, 1)
        self.assertEqual(m1.suit, Suit.MAN)
        self.assertEqual(str(m1), "1m")
        self.assertFalse(m1.red)

        p9 = Pinsu(9)
        self.assertEqual(p9.rank, 9)
        self.assertEqual(p9.suit, Suit.PIN)
        self.assertEqual(str(p9), "9p")
        self.assertFalse(p9.red)

        s5 = Sousu(5)
        self.assertEqual(s5.rank, 5)
        self.assertEqual(s5.suit, Suit.SOU)
        self.assertEqual(str(s5), "5s")
        self.assertFalse(s5.red)

    def test_red_fives(self):
        """Tests the red five (aka) logic."""
        red_5m = Mansu(0)
        self.assertEqual(red_5m.rank, 5)
        self.assertEqual(red_5m.suit, Suit.MAN)
        self.assertTrue(red_5m.red)
        self.assertEqual(str(red_5m), "5m")

        red_5p = Pinsu(0)
        self.assertEqual(red_5p.rank, 5)
        self.assertEqual(red_5p.suit, Suit.PIN)
        self.assertTrue(red_5p.red)
        self.assertEqual(str(red_5p), "5p")

        red_5s = Sousu(0)
        self.assertEqual(red_5s.rank, 5)
        self.assertEqual(red_5s.suit, Suit.SOU)
        self.assertTrue(red_5s.red)
        self.assertEqual(str(red_5s), "5s")

    def test_honor_tiles_and_aliases(self):
        """Tests Wind and Dragon tiles, and their aliases."""
        # Winds and Aliases
        winds = [
            (Ton, East, "1z"),
            (Nan, South, "2z"),
            (Sha, West, "3z"),
            (Pei, North, "4z"),
        ]
        for Original, Alias, str_rep in winds:
            with self.subTest(tile=Original.__name__):
                original_tile = Original()
                alias_tile = Alias()

                self.assertEqual(str(original_tile), str_rep)
                self.assertIsInstance(original_tile, Wind)
                self.assertIsInstance(original_tile, Honor)
                self.assertEqual(original_tile, alias_tile)
                self.assertIsInstance(alias_tile, Original)
                self.assertIsInstance(original_tile, Alias)

        # Dragons and Aliases
        dragons = [
            (Haku, White, "5z"),
            (Hatsu, Green, "6z"),
            (Chun, Red, "7z"),
        ]
        for Original, Alias, str_rep in dragons:
            with self.subTest(tile=Original.__name__):
                original_tile = Original()
                alias_tile = Alias()

                self.assertEqual(str(original_tile), str_rep)
                self.assertIsInstance(original_tile, Dragon)
                self.assertIsInstance(original_tile, Honor)
                self.assertEqual(original_tile, alias_tile)
                self.assertIsInstance(alias_tile, Original)
                self.assertIsInstance(original_tile, Alias)

    def test_dora_indicator(self):
        """Tests the dora indicator logic."""
        test_cases = [
            # (Indicator Tile, Expected Dora Tile)
            # Numbered suits
            (Pinsu(3), Pinsu(4)),
            (Mansu(8), Mansu(9)),
            (Sousu(9), Sousu(1)),  # Wrap-around
            # Red fives
            (Mansu(0), Mansu(6)),  # Red 5m -> 6m
            (Pinsu(5), Pinsu(6)),  # Normal 5p -> 6p
            # Winds
            (Ton(), Nan()),        # East -> South
            (Sha(), Pei()),        # West -> North
            (Pei(), Ton()),        # North -> East (wrap-around)
            # Dragons
            (Haku(), Hatsu()),     # White -> Green
            (Hatsu(), Chun()),     # Green -> Red
            (Chun(), Haku()),      # Red -> White (wrap-around)
        ]

        for indicator, expected_dora in test_cases:
            with self.subTest(indicator=str(indicator)):
                self.assertEqual(indicator.dora(), expected_dora)

    def test_is_terminal(self):
        """Tests the is_terminal method."""
        test_cases = [
            # (Tile, is_terminal)
            (Mansu(1), True), (Mansu(9), True),
            (Pinsu(1), True), (Pinsu(9), True),
            (Sousu(1), True), (Sousu(9), True),
            (Mansu(2), False), (Pinsu(5), False), (Sousu(8), False),
            (Mansu(0), False),  # Red 5m is not a terminal
            (Ton(), False),     # Winds are not terminals
            (Haku(), False),    # Dragons are not terminals
        ]

        for tile, expected in test_cases:
            with self.subTest(tile=str(tile)):
                self.assertEqual(tile.is_terminal(), expected)

if __name__ == '__main__':
    unittest.main()