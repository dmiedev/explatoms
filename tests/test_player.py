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

from explatoms.player import Player


class TestPlayer(unittest.TestCase):
    def test_get_opponent(self):
        self.assertEqual(Player(0).get_opponent(), Player(1))
        self.assertEqual(Player(1).get_opponent(), Player(0))