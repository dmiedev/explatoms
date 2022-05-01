# Copyright (C) 2021 Dmitry Egorov
#
# This file is part of Explatoms.
#
# Explatoms is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Explatoms is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Explatoms.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from explatoms.game import FieldType, Game
from explatoms.player import Player
from explatoms.square import SquareType


class TestFieldType(unittest.TestCase):
    def test_get_size(self):
        self.assertEqual(FieldType.SMALL.get_size(), 5)
        self.assertEqual(FieldType.MEDIUM.get_size(), 8)
        self.assertEqual(FieldType.BIG.get_size(), 11)
        self.assertEqual(FieldType.HUGE.get_size(), 14)


class TestGame(unittest.TestCase):
    __FIELD_TYPE = FieldType.SMALL

    def setUp(self):
        self.__player = Player(0)
        self.__atom_numbers = dict()
        self.__ownership = dict()
        self.__winner = None
        self.__game = Game(self.__FIELD_TYPE)
        self.__game.connect("current-player-change",
                            self.__remember_current_player)
        self.__game.connect("square-change",
                            self.__remember_square_change)
        self.__game.connect("is-over", self.__remember_winner)

    def __remember_current_player(self, game, current_player):
        self.__player = current_player

    def __remember_square_change(self, game, x, y, atom_number, owner):
        self.__atom_numbers[(x, y)] = atom_number
        self.__ownership[(x, y)] = owner

    def __remember_winner(self, game, winner):
        self.__winner = winner

    def test_square_ownership(self):
        self.assertTrue(self.__game.place_atom(0, 0))
        self.assertFalse(self.__game.place_atom(0, 0))
        self.assertTrue(self.__game.place_atom(0, 1))
        self.assertFalse(self.__game.place_atom(0, 1))

    def test_current_player_change(self):
        self.assertEqual(self.__player, Player(0))
        self.__game.place_atom(0, 0)
        self.assertEqual(self.__player, Player(1))
        self.__game.place_atom(0, 1)
        self.assertEqual(self.__player, Player(0))
        self.__game.place_atom(0, 1)
        self.assertEqual(self.__player, Player(0))

    def test_square_changes(self):
        self.__atom_numbers[(1, 1)] = 0
        self.__atom_numbers[(1, 2)] = 0
        for _ in range(SquareType.DEFAULT.get_capacity()):
            before = self.__atom_numbers[(1, 1)]
            self.__game.place_atom(1, 1)
            self.assertEqual(self.__atom_numbers[(1, 1)], before + 1)
            before = self.__atom_numbers[(1, 2)]
            self.__game.place_atom(1, 2)
            self.assertEqual(self.__atom_numbers[(1, 1)], before + 1)

    def test_corner_explosions(self):
        last = self.__FIELD_TYPE.get_size() - 1
        for _ in range(SquareType.CORNER.get_capacity() + 1):
            self.__game.place_atom(0, 0)
            self.__game.place_atom(last, last)
        self.assertEqual(self.__atom_numbers[(0, 0)], 0)
        self.assertEqual(self.__atom_numbers[(last, last)], 0)
        self.assertEqual(self.__atom_numbers[(1, 0)], 1)
        self.assertEqual(self.__atom_numbers[(0, 1)], 1)
        self.assertEqual(self.__atom_numbers[(last - 1, last)], 1)
        self.assertEqual(self.__atom_numbers[(last, last - 1)], 1)

    def test_wall_explosions(self):
        last = self.__FIELD_TYPE.get_size() - 1
        for _ in range(SquareType.WALL.get_capacity() + 1):
            self.__game.place_atom(last - 1, 0)
            self.__game.place_atom(1, last)
        self.assertEqual(self.__atom_numbers[(last - 1, 0)], 0)
        self.assertEqual(self.__atom_numbers[(1, last)], 0)
        self.assertEqual(self.__atom_numbers[(last - 2, 0)], 1)
        self.assertEqual(self.__atom_numbers[(0, last)], 1)
        self.assertEqual(self.__atom_numbers[(last, 0)], 1)
        self.assertEqual(self.__atom_numbers[(2, last)], 1)
        self.assertEqual(self.__atom_numbers[(last - 1, 1)], 1)
        self.assertEqual(self.__atom_numbers[(1, last - 1)], 1)

    def test_default_explosions(self):
        last = self.__FIELD_TYPE.get_size() - 1
        for _ in range(SquareType.DEFAULT.get_capacity() + 1):
            self.__game.place_atom(1, 1)
            self.__game.place_atom(last - 1, last - 1)
        self.assertEqual(self.__atom_numbers[(1, 1)], 0)
        self.assertEqual(self.__atom_numbers[(last - 1, last - 1)], 0)
        for e in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            self.assertEqual(self.__atom_numbers[(1 + e[0], 1 + e[1])], 1)
            self.assertEqual(self.__atom_numbers[(
                last - 1 + e[0], last - 1 + e[1])], 1)

    def test_complex_explosions(self):
        for _ in range(SquareType.CORNER.get_capacity() + 1):
            self.__game.place_atom(0, 1)
            self.__game.place_atom(0, 0)
        for i in ((0, 0), (1, 0), (1, 1), (0, 2)):
            self.assertEqual(self.__atom_numbers[i], 1)
            self.assertEqual(self.__ownership[i], Player(1))
        self.assertEqual(self.__atom_numbers[(0, 1)], 0)
        self.assertIsNone(self.__ownership[(0, 1)])

        for _ in range(SquareType.DEFAULT.get_capacity() + 1):
            self.__game.place_atom(1, 3)
            self.__game.place_atom(2, 3)
        for i in ((0, 3), (1, 2), (1, 3), (1, 4), (2, 2), (2, 4), (3, 3)):
            self.assertEqual(self.__atom_numbers[i], 1)
            self.assertEqual(self.__ownership[i], Player(0))
        self.assertEqual(self.__atom_numbers[(2, 3)], 1)
        self.assertEqual(self.__ownership[(2, 3)], Player(1))

    def test_game_over(self):
        field_size = self.__FIELD_TYPE.get_size()
        counter = 0
        max_atoms = ((field_size - 2)**2 * 3) + ((field_size - 2) * 4 * 2) + 4
        while self.__winner is None:
            self.__game.place_atom(0, 0)
            self.__game.place_atom(field_size - 1, field_size - 1)
            counter += 2
            if counter >= max_atoms:
                break
        self.assertEqual(self.__winner, Player(0))
        self.assertLess(counter, max_atoms)
