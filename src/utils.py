import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from subprocess import Popen
from sources import get_remote_source, remote_workflow
progressbar = Gtk.ProgressBar()

def shell(cmd):
  return Popen(cmd)

def remove_autostart():
  first_run = "/etc/xdg/autostart/io.jde.postinstall-wizard.desktop"
  if os.path.exists(first_run):
      from utils import shell
      shell(["pkexec", "rm", "-f", first_run])
                            
def set_progress(progress):
  if progress:
    progressbar.set_fraction(progress)
  else:
    progressbar.pulse()        

def update_mirrors():    
    shell(["pkexec", "pacman-mirrors", "--fasttrack"])  
    
def run_postinstall():
  postinstall = "/usr/share/jde-postinstall-wizard/scripts/postinstall"
  if os.path.exists(postinstall):
     print("Running post installation")
     p = shell(postinstall)
     p.wait()
  else:
     print("post install script not found")  
     
