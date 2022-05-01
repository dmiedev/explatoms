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


class Player(Enum):
    """A player enumeration."""

    #: The blue player.
    BLUE = 0

    #: The red player.
    RED = 1

    def get_opponent(self) -> "Player":
        """Retrieve the opponent player of `self`.

        :returns: The opponent of `self`.
        :rtype: `Player`
        """
        return Player(1 - self.value)