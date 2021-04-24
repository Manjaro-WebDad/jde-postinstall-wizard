import gi
import time
import utils
import dialog
from importlib import reload
gi.require_version("Gtk", "3.0")
gi.require_version('Pamac', '10.0')
from sources import load_yaml
from gi.repository import GLib, Pamac as p

class Pamac:
    def __init__(self):
        self.packages = []
        config = p.Config(conf_path="/etc/pamac.conf")
        config.set_enable_aur(False)
        self.db = p.Database(config=config)
        self.db.enable_appstream()
        self.transaction = p.Transaction(database=self.db)
        self.transaction.connect("emit-action", self.on_emit_action, self.packages)
        self.transaction.connect("emit-action-progress", self.on_emit_action_progress, self.packages)
        self.transaction.connect("emit-hook-progress", self.on_emit_hook_progress, self.packages)
        self.transaction.connect("emit-error", self.on_emit_error, self.packages)
        self.transaction.connect("emit-warning", self.on_emit_warning, self.packages)        
        self.loop = GLib.MainLoop()
        #for i in dir(self.transaction):
        #  print(i)

 
    def get_app_icon(self, pkg):
        return self.db.get_pkg(pkg).get_icon()

    def get_app_name(self, pkg):
        name = self.db.get_pkg(pkg).get_app_name()
        if not name:
          name = self.db.get_pkg(pkg).get_name()
        if not name:
          name = f"package not existent: {pkg}"
          print("package not existent:", pkg)
        return name

    def pkg_exists(self, pkg):
      try: 
        if self.db.get_pkg(pkg).get_name() == pkg:
          return True 
        else:
          return False
      except AttributeError:
        return False

    def check_packages(self, packages):
      
        def check_pkg(pkg):
          if self.pkg_exists(pkg):
            if pkg not in self.get_installed_pkgs():
                self.packages.append(pkg)
          else:
            print("package not existent:", pkg)
                  
        if packages != None:  
          if isinstance(packages, (list, tuple)):       
            for pkg in packages:
              check_pkg(pkg)              
          else:
            check_pkg(packages)
        
    def get_installed_pkgs(self):
      pkgs = []
      for pkg in self.db.get_installed_pkgs():
        pkgs.append( pkg.get_name() )
      return pkgs

    def on_emit_action(self, transaction, action, data):
       print(action)

    def on_emit_action_progress(self, transaction, action, status, progress, data):
        print(f"{action} {status} {progress}")
        if self.timeout:
           GLib.source_remove(self.timeout)
           self.timeout = False
        utils.set_progress(progress)      

    def on_emit_hook_progress(self, transaction, action, details, status, progress, data):
        print(f"{action} {details} {status}")
        utils.set_progress(progress)

    def on_emit_warning(self, transaction, message, data):
        print(message)

    def on_emit_error(self, transaction, message, details, details_length, data):
        if details_length > 0:
          print(f"{message}:")
        for detail in details:
          print(detail)
        else:
          print(message)

    def on_transaction_finished_callback(self, source_object, result, user_data):
       try:
         success = source_object.run_finish(result)
       except GLib.GError as e:
         print("Error: ", e.message)
       else:
         if success:
            utils.run_postinstall()
            dialog.Modal().start()
            utils.remove_autostart()
         else:
            print("Ops something went wrong.")
       finally:
         self.loop.quit()
         self.transaction.quit_daemon()
    
    def run_transaction(self): 
        self.transaction.add_pkgs_to_upgrade(self.db.get_installed_pkgs())
        for pkg in self.packages:
            self.transaction.add_pkg_to_install(pkg)

        self.transaction.run_async(self.on_transaction_finished_callback, None)
        self.loop.run()

    def on_timeout(self, *args):
        utils.set_progress(0)
        return True

    def install(self):
      if self.packages:
         self.timeout = GLib.timeout_add(50, self.on_timeout, None)
         print(f"selected packages:{self.packages}")
         self.run_transaction()       
