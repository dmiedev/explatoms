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

import typeguard 

from explatoms import drawing


class TestDrawing(unittest.TestCase):
    def test_get_circle_draw_callback(self):
        min, max = 1, 3
        self.assertIsNone(drawing.get_circle_draw_callback(min - 1)) 
        for i in range(min, max + 1):
            callback = drawing.get_circle_draw_callback(i)
            typeguard.check_type("callback", callback, drawing.DrawCallback)
        self.assertIsNone(drawing.get_circle_draw_callback(max + 1))
        
        