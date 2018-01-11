import logging
import gi
import gpg

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


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
        filename = data.get_text()
        logger.info("Received file: %s" % filename)
        filename = filename[7:].strip('\r\n\x00')  # remove file://, \r\n and NULL
        try:
            result = self.import_key(filename)
        except gpg.errors.GPGMEError as e:
            logger.error(e)
            result = "An error occurred, please try again"
        self.go_to_result(result)

    def on_select_button_clicked(self, button):
        file_chooser = self.builder.get_object("file_chooser")
        filename = file_chooser.get_filename()
        logger.info("Selected file: %s" % filename)
        try:
            result = self.import_key(filename)
        except gpg.errors.GPGMEError as e:
            logger.error(e)
            result = "An error occurred, please try again"
        self.go_to_result(result)

    def go_to_result(self, result):
        result_label = self.builder.get_object("sign_result")
        result_label.set_text(result)
        stack = self.builder.get_object("companion_stack")
        stack.set_visible_child_name("result")

    @staticmethod
    def import_key(filename):
        ctx = gpg.Context()
        with open(filename, "rb") as fh:
            decrypted = ctx.decrypt(fh)
        ctx.op_import(decrypted[0])
        result = ctx.op_import_result()
        if len(result.imports) > 0:
            return "Signed key successfully imported"
        else:
            raise gpg.errors.GPGMEError


GUI()
Gtk.main()
