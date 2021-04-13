import gi
import os
import asyncio
from subprocess import PIPE, Popen
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from sources import get_remote_source, remote_workflow
progressbar = Gtk.ProgressBar()

def shell(cmd, shell=False):
  return Popen(cmd, shell=shell)

def get_branch():
    with open("/etc/pacman-mirrors.conf", "r") as f:
      for line in f:
        if "Branch = " in line:        
            branch = line.replace("Branch = ", "").replace("#", "").strip()
            return branch
    
def set_branch_mirrors(branch):
  cmd = ["pkexec", "pacman-mirrors", "--fasttrack", "--api", "--set-branch", f"{branch}"]
  shell(cmd)

def remove_autostart():
  first_run = "/etc/xdg/autostart/io.jde.postinstall-wizard.desktop"
  if os.path.exists(first_run):
      shell(["pkexec", "rm", "-f", first_run])
                            
def set_progress(progress):
  if progress:
    progressbar.set_fraction(progress)
  else:
    progressbar.pulse()        

def run_postinstall():
  postinstall = "/usr/share/jde-postinstall-wizard/scripts/postinstall"
  if os.path.exists(postinstall):
     print("Running post installation")
     p = shell(postinstall)
     p.wait()
  else:
     print("post install script not found")  
     
