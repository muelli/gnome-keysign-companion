import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import logging


DRAG_ACTION = Gdk.DragAction.COPY

logger = logging.getLogger(__name__)


class GUI:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('window.glade')
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("appwindow")
        self.window.show()

        self.label = self.builder.get_object("drop_here")

        self.label.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.label.drag_dest_set_target_list(None)
        self.label.drag_dest_add_text_targets()

    @staticmethod
    def on_delete_window(*args):
        Gtk.main_quit(*args)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        text = data.get_text()
        print("Received text: %s" % text)

    def on_select_button_clicked(self, button):
        pass


GUI()
Gtk.main()
