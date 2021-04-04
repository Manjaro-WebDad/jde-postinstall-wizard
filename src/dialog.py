import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from utils import shell


class Modal(Gtk.Dialog):
    def __init__(self, parent=None):
        Gtk.Dialog.__init__(self, title="", transient_for=parent, flags=0)        
        self.add_buttons(
            "Quit",  Gtk.ResponseType.CLOSE, "Reboot", Gtk.ResponseType.OK, "Install Additional Software", Gtk.ResponseType.CANCEL
        )
        self.fullscreen()
        label = Gtk.Label(label="All Done, you should reboot after a upgrade.")
        label.get_style_context().add_class("large-fonts")
        label.get_style_context().add_class("reboot-label")
        box = self.get_content_area()
        box.props.valign = box.props.halign = Gtk.Align.CENTER
        box.add(label)
        box.get_style_context().add_class("modal")
        self.show_all()
    
    def start(self):        
        response = self.run()
        if response == Gtk.ResponseType.OK:
            shell(['systemctl', 'reboot'])
        elif response == Gtk.ResponseType.CLOSE:
            self.quit()
            
        elif response == Gtk.ResponseType.CANCEL:
            shell(["pamac-manager"])
            self.quit()
            
    def quit(self):
        Gtk.main_quit()
