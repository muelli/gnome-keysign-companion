import logging
import mailbox

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
        self.eventbox = self.builder.get_object("eventbox")

        self.label.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.label.drag_dest_set_target_list(None)
        self.label.drag_dest_add_text_targets()
        self.label.drag_dest_add_uri_targets()

        select = self.builder.get_object("select_button")
        list_targets = []
        if False:
            list_targets = Gtk.TargetList.new([])
            [
                #Gtk.TargetEntry("text/uri-list"),
                Gtk.TargetEntry.new("text/plain"),
                #Gtk.TargetEntry("TEXT"),
            ]
        select.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, list_targets, DRAG_ACTION)
        #select.drag_source_add_text_targets()
        select.drag_source_add_uri_targets()
        # select.drag_source_set_target_list(Gtk.TargetList.new([Gtk.TargetEntry()]))
        select.connect("drag-data-get", self.on_drag_data_get)
        #select.connect("drag-begin", self.on_drag_begin)

    def on_drag_begin(self, label, drag_context):
        logger.warning("Info: %r", drag_context)
        return drag_context

    def on_drag_data_get(self, label, drag_context, data, info, time):
        logger.info("Info: %r", info)
        logger.info("Time: %r", time)
        logger.info("Data: %r", data)
        data.set_text("Hello", -1)
        fname = "/tmp/foo"
        with open(fname, 'w') as fh:
            fh.write("Bar!")
        data.set_uris(["/tmp/foo"])

    @staticmethod
    def on_delete_window(*args):
        Gtk.main_quit(*args)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        filename = data.get_text()
        # If we don't have a filename it means that the user maybe dropped
        # an attachment or an entire email.
        if not filename:
            filename = data.get_data().decode("utf-8")
        logger.info("Received file: %s" % filename)
        filename = filename[7:].strip('\r\n\x00')  # remove file://, \r\n and NULL
        signatures = self.get_attachments(filename)
        # If there aren't attachments probably we have directly the signature
        if not signatures:
            with open(filename, "rb") as si:
                signatures.append(si.read())
            si.close()

        result = None
        try:
            for signature in signatures:
                result = self.import_key(signature)
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
        back_button = self.builder.get_object("back_button")
        back_button.set_sensitive(True)
        stack = self.builder.get_object("companion_stack")
        stack.set_visible_child_name("result")

    def on_back_button_clicked(self, button):
        back_button = self.builder.get_object("back_button")
        back_button.set_sensitive(False)
        stack = self.builder.get_object("companion_stack")
        stack.set_visible_child_name("select_key")

    def on_file_set(self, button):
        select = self.builder.get_object("select_button")
        select.set_sensitive(True)

    @staticmethod
    def import_key(signature):
        ctx = gpg.Context()
        decrypted = ctx.decrypt(signature)
        ctx.op_import(decrypted[0])
        result = ctx.op_import_result()
        if len(result.imports) > 0:
            return "Signed key successfully imported"
        else:
            raise gpg.errors.GPGMEError

    @staticmethod
    def get_attachments(filename):
        mbox = mailbox.mbox(filename)
        attachments = []
        for message in mbox:
            # Check if there are attachments
            if message.is_multipart():
                for attach in message.get_payload()[1:]:
                    attachments.append(attach.get_payload(decode=True))
        return attachments

logging.basicConfig(level=logging.DEBUG)
GUI()
Gtk.main()
