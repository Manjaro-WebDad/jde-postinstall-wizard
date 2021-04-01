import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from subprocess import Popen
progressbar = Gtk.ProgressBar()


def set_progress(progress):
  if progress:
    progressbar.set_fraction(progress)
  else:
    progressbar.pulse()        

def update_mirrors():    
    Popen(["pkexec", "pacman-mirrors", "--fasttrack"])     
    
