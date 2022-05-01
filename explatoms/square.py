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

from explatoms.player import Player


class SquareType(Enum):
    """A square type enumeration."""

    #: The default (middle) square.
    DEFAULT = 0

    #: The wall square (located beside a wall).
    WALL = 1

    #: The corner square.
    CORNER = 2

    def get_capacity(self) -> int:
        """Retrieve the capacity of `self`.

        :returns: The capacity of `self`.
        :rtype: `int`
        """
        return 3 - self.value


class Square:
    """A square of a field.
    
    :param SquareType type: The square type.
    
    :ivar int __atom_number: The number of atoms on `self`.
    :ivar Player __owner: The owner of atoms on `self`.
    :ivar SquareType __type: The type of `self`.
    """
    
    def __init__(self, type: SquareType) -> None:
        """Initiate a `Square` object with the given type.
        
        :param SquareType type: The square type.
        :rtype: `None`
        """
        self.__atom_number = 0
        self.__owner = None
        self.__type = type

    def add_atom(self, player: Player) -> bool:
        """Add a player's atom to `self`.
        
        :param Player player: The player who adds the atom.
        :returns: `True` if `self` has become full, `False` otherwise.
        :rtype: `bool`
        
        This will make player own all atoms on `self`.
        
        `self` becomes full when the capacity as defined by its type
        is reached, in which case its properties are set to default values.
        """
        self.__atom_number += 1
        self.__owner = player
        if self.__atom_number > self.__type.get_capacity():
            self.__atom_number = 0
            self.__owner = None
            return True
        return False

    def get_atom_number(self) -> int:
        """Retrieve the number of atoms on `self`.
        
        :returns: The number of atoms on `self`.
        :rtype: `int`
        """
        return self.__atom_number

    def get_owner(self) -> Player:
        """Retrieve the owner of atoms on `self`.
        
        :returns: The owner of atoms on `self`.
        :rtype: `Player`
        """
        return self.__owner