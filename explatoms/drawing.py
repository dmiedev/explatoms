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

from math import pi
from typing import Callable

import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from explatoms import colors


#: A `Gtk.DrawingArea::draw` callback.
DrawCallback = Callable[[Gtk.DrawingArea, cairo.Context, colors.Color], None]

def __get_drawing_area_size(area: Gtk.DrawingArea) -> tuple[int, int]:
    """Retrieve the width and the height of a drawing area.
    
    :param Gtk.DrawingArea area: The drawing area.
    :returns: The width and the height of the drawing area.
    :rtype: `tuple[int, int]`
    """
    return area.get_allocated_width(), area.get_allocated_height()

def __draw_one(area: Gtk.DrawingArea,
               context: cairo.Context, color: colors.Color) -> None:
    """Draw one circle in a drawing area.
    
    :param Gtk.DrawingArea area: The drawing area.
    :param cairo.Context context: Cairo context.
    :param colors.Color color: A color in which to draw.
    :rtype: `None`
    """
    x, y = __get_drawing_area_size(area)
    __draw_circle(context, x / 2, y / 2, color)

def __draw_two(area: Gtk.DrawingArea,
               context: cairo.Context, color: colors.Color) -> None:
    """Draw two circles in a drawing area.
    
    :param Gtk.DrawingArea area: The drawing area.
    :param cairo.Context context: Cairo context.
    :param colors.Color color: A color in which to draw.
    :rtype: `None`
    """
    x, y = __get_drawing_area_size(area)
    __draw_circle(context, x / 4, y / 2, color)
    __draw_circle(context, x / 4 * 3, y / 2, color)

def __draw_three(area: Gtk.DrawingArea,
                 context: cairo.Context, color: colors.Color) -> None:
    """Draw three circles in a drawing area.
    
    :param Gtk.DrawingArea area: The drawing area.
    :param cairo.Context context: Cairo context.
    :param colors.Color color: A color in which to draw.
    :rtype: `None`
    """
    x, y = __get_drawing_area_size(area)
    __draw_circle(context, x / 2, y / 3, color)
    __draw_circle(context, x / 4, y / 3 * 2, color)
    __draw_circle(context, x / 4 * 3, y / 3 * 2, color)

def __draw_circle(context: cairo.Context,
                  x: int, y: int, color: colors.Color) -> None:
    """Draw a circle at given coordinates using given context.
    
    :param cairo.Context context: Cairo context.
    :param int x: An x coordinate.
    :param int y: An y coordinate.
    :param colors.Color color: A color in which to draw.
    :rtype: `None`
    """
    context.set_source_rgb(*color)
    context.arc(x, y, 7.5, 0, 2 * pi)
    context.fill()

def get_circle_draw_callback(circle_number: int) -> DrawCallback:
    """Retrieve a `Gtk.DrawingArea::draw` callback that draws a given number
    of circles.
    
    :param int circle_number: A number of circles to be drawn, in range 1-3.
    :returns: A `Gtk.DrawingArea::draw` callback or `None` if `circle_number`
        is not in range 1-3.
    :rtype: `DrawCallback` or `None`
    """
    circle_drawers = [__draw_one, __draw_two, __draw_three]
    if circle_number < 1 or circle_number > len(circle_drawers):
        return None
    return circle_drawers[circle_number - 1]
