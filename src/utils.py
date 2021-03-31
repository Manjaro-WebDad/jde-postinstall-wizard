import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from subprocess import run

progressbar = Gtk.ProgressBar()

def update_mirrors():
    run(["pkexec", "pacman-mirrors", "--fasttrack"])
