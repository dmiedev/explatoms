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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from explatoms import colors
from explatoms import drawing
from explatoms.game import Game, FieldType
from explatoms.player import Player


class UIHandler:
    """A user interface handler.
    
    :param Game game: A game to start with.
    
    :ivar Game __game: The current game.
    :ivar Gtk.Builder __builder: The builder used to access widgets.
    :ivar dict[tuple[int, int], int] __square_draw_callback_ids: 
        IDs of "draw" callback of squares' drawing areas.
    """
    
    #: The size of the square widget.
    __SQUARE_SIZE = 50
    #: Colors of the players.
    __PLAYER_COLORS = {Player.BLUE: colors.BLUE, Player.RED: colors.RED}

    def __init__(self, game: Game) -> None:
        """Initiate a `UIHandler` object.
        
        :param Game game: A game to start with.
        :rtype: `None`
        """
        self.__game = game
        self.__connect_game_signals()
        self.__load()
        self.__create_squares()
        self.__show_window()

    def __load(self) -> None:
        """Load the user interface.
        
        :rtype: `None`
        """
        self.__builder = Gtk.Builder()
        self.__builder.add_from_file("data/explatoms.glade")
        self.__builder.connect_signals(self)
        self.__load_styles()

    def __connect_game_signals(self) -> None:
        """Connect to the signals of the game.
        
        :rtype: `None`
        """
        self.__game.connect("is-over", self.__on_game_over)
        self.__game.connect("square-change", self.__on_square_change)
        self.__game.connect("current-player-change",
                            self.__on_current_player_change)

    def __create_squares(self) -> None:
        """Create squares and attach them to the field.
        
        :rtype: `None`
        """
        field = self.__builder.get_object("field")
        field_size = self.__game.get_field_type().get_size()
        self.__square_draw_callback_ids = dict()
        for i in range(field_size):
            for j in range(field_size):
                square = Gtk.Button()
                square.set_size_request(self.__SQUARE_SIZE, self.__SQUARE_SIZE)
                square.get_style_context().add_class("square")
                square.connect("clicked", self.on_square_clicked, i, j)
                square.add(Gtk.DrawingArea())
                field.attach(square, i, j, 1, 1)
        field.show_all()

    def __load_styles(self) -> None:
        """Load CSS style sheets written for widget customization.
        
        :rtype: `None`
        """
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        provider.load_from_path("data/styles.css")

    def __show_window(self) -> None:
        """Show the main window.
        
        :rtype: `None`
        """
        window = self.__builder.get_object("window")
        window.show_all()

    def run(self) -> None:
        """Run the GTK main loop.
        
        :rtype: `None`
        """
        Gtk.main()

    def on_square_clicked(self, square: Gtk.Button, x: int, y: int) -> None:
        """Handle a click on the square with given coordinates.
        
        :param Gtk.Button square: The square.
        :param int x: The x coordinate.
        :param int y: The y coordinate.
        :rtype: `None`
        """
        self.__game.place_atom(x, y)

    def on_window_destroy(self, window: Gtk.Window) -> None:
        """Handle the destruction of the main window.
        
        :param Gtk.Window window: The main window.
        :rtype: `None`
        """
        Gtk.main_quit()

    def on_about_menu_button_clicked(self, button: Gtk.ModelButton) -> None:
        """Handle a click on the About menu button.
        
        :param Gtk.ModelButton button: The About menu button.
        :rtype: `None`
        """
        about_dialog = self.__builder.get_object("about_dialog")
        about_dialog.run()
        about_dialog.hide()

    def on_new_game_menu_button_clicked(self, button: Gtk.ModelButton) -> None:
        """Handle a click on the New Game menu button.
        
        :param Gtk.ModelButton button: The New Game menu button.
        :rtype: `None`
        """
        new_game_dialog = self.__builder.get_object("new_game_dialog")
        response = new_game_dialog.run()
        if response == Gtk.ResponseType.OK:
            self.__create_new_game()
        new_game_dialog.hide()

    def __create_new_game(self) -> None:
        """Create a new game with the chosen field type.
        
        :rtype: `None`
        
        The field type is read from the field type combobox located
        in the new game dialog.
        """
        combo_box = self.__builder.get_object("field_size_combo_box")
        field_type = FieldType(combo_box.get_active())
        self.__game = Game(field_type=field_type)
        self.__on_current_player_change(self.__game, Player(0))
        self.__connect_game_signals()
        self.__destroy_squares()
        self.__create_squares()

    def __destroy_squares(self) -> None:
        """Destroy all squares of the field.
        
        :rtype: `None`
        """
        field = self.__builder.get_object("field")
        field.foreach(lambda square: square.destroy())

    def __disable_squares(self) -> None:
        """Disable all squares of the field.
        
        :rtype: `None`
        """
        field = self.__builder.get_object("field")
        field.foreach(lambda square: square.set_sensitive(False))

    def __on_game_over(self, game: Game, winner: Player) -> None:
        """Handle the end of the game.
        
        :param Game game: The game.
        :param Player winner: The player who has won.
        :rtype: `None`
        """
        self.__disable_squares()
        self.__set_window_subtitle(f"{winner.name.title()} won!")
        game_over_dialog = self.__builder.get_object("game_over_dialog")
        game_over_dialog.set_property("text", f"{winner.name.title()} wins!")
        game_over_dialog.run()
        game_over_dialog.hide()

    def __on_square_change(self, game: Game, x: int, y: int,
                           atom_number: int, player: Player) -> None:
        """Handle the change of a square with given coordinates and number of
        atoms.
        
        :param Game game: The game.
        :param int x: The x coordinate of the square.
        :param int y: The y coordinate of the square.
        :param int atom_number: The number of atoms on the square.
        :param Player player: The current player.
        :rtype: `None`
        
        This causes the square with the given coordinates to be redrawn with
        the new number of atoms.
        """
        field = self.__builder.get_object("field")
        square = field.get_child_at(x, y)
        drawing_area = square.get_children()[0]
        if (x, y) in self.__square_draw_callback_ids:
            # Disconnect a previous "draw" callback from square's
            # drawing area.
            drawing_area.disconnect(self.__square_draw_callback_ids[(x, y)])
            del self.__square_draw_callback_ids[(x, y)]
        if atom_number > 0:
            # Connect a new "draw" callback to square's drawing area.
            draw_callback = drawing.get_circle_draw_callback(atom_number)
            self.__square_draw_callback_ids[(x, y)] = drawing_area.connect(
                "draw", draw_callback, self.__PLAYER_COLORS[player])
        drawing_area.queue_draw()

    def __on_current_player_change(self, game: Game, player: Player) -> None:
        """Handle the change of the current player.
        
        :param Game game: The game.
        :param Player player: The current player.
        :rtype: `None`
        """
        self.__set_window_subtitle(f"{player.name.title()}'s move")

    def __set_window_subtitle(self, subtitle: str) -> None:
        """Set the subtitle of the main window to subtitle.
        
        :param str subtitle: The subtitle.
        :rtype: `None`
        """
        header_bar = self.__builder.get_object("header_bar")
        header_bar.set_subtitle(subtitle)
