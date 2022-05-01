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

from enum import Enum
from typing import Iterable

import gi
from gi.repository import GObject

from explatoms.player import Player
from explatoms.square import Square, SquareType


class FieldType(Enum):
    """A field type enumeration."""

    #: The small field.
    SMALL = 0

    #: The medium field.
    MEDIUM = 1

    #: The big field.
    BIG = 2

    #: The huge field.
    HUGE = 3

    def get_size(self) -> int:
        """Retrieve the size of `self`.

        :returns: The size of `self`.
        :rtype: `int`

        This is meant to be the length of a side of a square field.
        """
        return 5 + self.value * 3


class Game(GObject.GObject):
    """A game that contains a field of squares.
    
    :param FieldType field_type: The field type, defaults to 
        `FieldType.MEDIUM`.
    
    :ivar FieldType __field_type: The field type used in `self`.
    :ivar Player __current_player: The player whose move it is now.
    :ivar list[list[Square]] __field: The field that is made out of squares.
    
    :GObject Signals:
    
    .. list-table::
       :header-rows: 1
       :widths: auto
    
       * - Name
         - Parameters
         - Description
       * - is-over
         - **winner** (*Player*) – The winner.
         - Is emitted when the game ends.
       * - square-change
         - - **x** (*int*) – The x coordinate of the square.
           - **y** (*int*) – The y coordinate of the square.
           - **atom_number** (*int*) – The number of atoms on the square.
           - **owner** (*Player*) – The owner of atoms on the square.
         - Is emitted when a square changes.
       * - current-player-change
         - **current_player** (*Player*) – The current player.
         - Is emitted when the current player changes.
    """
    
    __gsignals__ = {
        "is-over": (GObject.SignalFlags.RUN_FIRST, None,
                    (GObject.TYPE_PYOBJECT, )),
        "square-change": (GObject.SignalFlags.RUN_FIRST, None,
                          (int, int, int, GObject.TYPE_PYOBJECT)),
        "current-player-change": (GObject.SignalFlags.RUN_FIRST, None,
                                  (GObject.TYPE_PYOBJECT, )),
    }

    def __set_current_player(self, player: Player) -> None:
        """Set the current player and notifies listeners of this change.
        
        :param Player player: The current player.
        :rtype: `None`
        """
        self.__current_player = player
        self.emit("current-player-change", self.__current_player)

    def __init__(self, field_type: FieldType = FieldType.MEDIUM) -> None:
        """Initiate a `Game` object with the given field type.
        
        :param FieldType field_type: The field type, defaults to 
            `FieldType.MEDIUM`.
        :rtype: `None`
        """
        super().__init__()
        self.__field_type = field_type
        self.__set_current_player(Player(0))
        self.__create_field()
        
    def __determine_square_type(self, x: int, y: int) -> SquareType:
        """Retrieve the type of a square according to its coordinates in the field.
        
        :param int x: The x coordinate.
        :param int y: The y coordinate.
        :returns: The square type.
        :rtype: `SquareType`
        """
        field_size = self.__field_type.get_size()
        walls = (x == 0 or x == field_size - 1, 
                 y == 0 or y == field_size - 1)
        if walls[0] and walls[1]:
            return SquareType.CORNER
        if walls[0] or walls[1]:
            return SquareType.WALL
        return SquareType.DEFAULT

    def __create_field(self) -> None:
        """Fill the field with squares.
        
        :rtype: `None`
        """
        self.__field = []
        field_size = self.__field_type.get_size()
        for i in range(field_size):
            self.__field.append([])
            for j in range(field_size):
                square = Square(self.__determine_square_type(i, j))
                self.__field[i].append(square)

    def get_field_type(self) -> FieldType:
        """Retrieve the type of the field used in `self`.
        
        :returns: The field type used in `self`.
        :rtype: `FieldType`
        """
        return self.__field_type

    def place_atom(self, x: int, y: int) -> bool:
        """Place an atom on the square with given coordinates on behalf
        of the current player.
        
        :param int x: The x coordinate of the square.
        :param int y: The y coordinate of the sqaure.
        :returns: `True` if the atom has been placed, `False` otherwise.
        :rtype: `bool`
        
        An atom cannot be placed on a square with opponent's atoms.
        
        This causes `square_change` signals to be emitted.
        If there are no available further moves, emits `is_over` signal.
        """
        opponent = self.__current_player.get_opponent()
        if self.__field[x][y].get_owner() == opponent:
            return False
        became_full = self.__field[x][y].add_atom(self.__current_player)
        self.emit("square-change", x, y,
                  self.__field[x][y].get_atom_number(),
                  self.__field[x][y].get_owner())
        if became_full:
            if self.__explode_atoms(x, y):
                self.emit("is-over", self.__current_player)
                return True
        self.__set_current_player(opponent)
        return True

    def __explode_atoms(self, x: int, y: int) -> bool:
        """Explode atoms from the square with given coordinates.
        
        :param int x: The x coordinate of the square.
        :param int y: The y coordinate of the square.
        :returns: `True` if this has resulted in an infinite loop of 
            explosions, `False` otherwise.
        :rtype: `bool`
        
        This explodes atoms until there is no full squares.
        
        This results in an infinite loop of explosions only if atoms
        of all squares have exploded.
        """
        queue = [(x, y)]
        changed_squares = set()
        field_size = self.__field_type.get_size()
        while queue:
            # If atoms of all squares have exploded, that means there
            # will be an infinite loop of explosions and we need to exit
            # the while-loop.
            if len(changed_squares) == field_size**2:
                self.__emit_square_changes(changed_squares)
                return True
            x_cur, y_cur = queue.pop(0)
            for explosion in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                x_e, y_e = x_cur + explosion[0], y_cur + explosion[1]
                if x_e not in range(0, field_size) or \
                        y_e not in range(0, field_size):
                    continue
                became_full = self.__field[x_e][y_e].add_atom(
                    self.__current_player)
                if became_full:
                    queue.append((x_e, y_e))
                changed_squares.add((x_e, y_e))
        self.__emit_square_changes(changed_squares)
        return False

    def __emit_square_changes(self, changed_squares: Iterable) -> None:
        """Notify listeners of changed squares.
        
        :param Iterable changed_squares: Squares that have changed.
        :rtype: `None`
        """
        for x, y in changed_squares:
            self.emit("square-change", x, y,
                      self.__field[x][y].get_atom_number(),
                      self.__field[x][y].get_owner())
