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

from explatoms.square import SquareType, Square
from explatoms.player import Player


class TestSquareType(unittest.TestCase):
    def test_get_capacity(self):
        self.assertEqual(SquareType.CORNER.get_capacity(), 1)
        self.assertEqual(SquareType.WALL.get_capacity(), 2)
        self.assertEqual(SquareType.DEFAULT.get_capacity(), 3)
        
        
class TestSquare(unittest.TestCase):
    def test_init(self):
        square = Square(SquareType(0))
        self.assertEqual(square.get_atom_number(), 0)
        self.assertIsNone(square.get_owner())
        
    def test_add_atom(self):
        for player in Player:
            for square_type in SquareType:
                square = Square(square_type)
                atom_number = square.get_atom_number()
                for _ in range(square_type.get_capacity()):
                    square.add_atom(player)
                    new_atom_number = square.get_atom_number()
                    self.assertEqual(new_atom_number, atom_number + 1)
                    atom_number = new_atom_number
                    self.assertEqual(square.get_owner(), player)
        
    def test_owner_change(self):
        square = Square(SquareType.DEFAULT)
        square.add_atom(Player(0))
        self.assertEqual(square.get_owner(), Player(0))
        square.add_atom(Player(1))
        self.assertEqual(square.get_owner(), Player(1))
        
    def test_capacity(self):
        for square_type in SquareType:
            square = Square(square_type)
            for _ in range(square_type.get_capacity() + 1):
                square.add_atom(Player(0))
            self.assertEqual(square.get_atom_number(), 0)
            self.assertIsNone(square.get_owner(), None)
            