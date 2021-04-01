import gi
gi.require_version('Pamac', '10.0')
from sources import load_yaml
from utils import set_progress
from utils import update_mirrors
from gi.repository import GLib, Pamac as p


class Pamac:
    def __init__(self):
        self.packages = []
        self.data = load_yaml()
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
        print(dir(self.transaction))
 
    def get_app_icon(self, pkg):
        return self.db.get_pkg(pkg).get_icon()

    def get_app_name(self, pkg):
        return self.db.get_pkg(pkg).get_app_name()

    def test_pkg(self, pkg):
        return self.db.get_pkg(pkg).get_name()

    def get_installed_pkgs(self):
        return self.db.get_installed_pkgs()

    def on_emit_action(self, transaction, action, data):
       print(action)

    def on_emit_action_progress(self, transaction, action, status, progress, data):
        print(f"{action} {status} {progress}")
        set_progress(progress)      

    def on_emit_hook_progress(self, transaction, action, details, status, progress, data):
        print(f"{action} {details} {status}")
        set_progress(progress)

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
         ##TODO run postinstall script.
         ## show all finish modal
       else:
         print("Success :", success)
       finally:
         self.loop.quit()
         self.transaction.quit_daemon()
    
    def run_transaction(self):        
        self.transaction.add_pkgs_to_upgrade(self.get_installed_pkgs())
        for pkg in self.packages:
            self.transaction.add_pkg_to_install(pkg)

        self.transaction.run_async(self.on_transaction_finished_callback, None)
        self.loop.run()

    def on_timeout(self, *args):
        set_progress(0)
        return True

    def install(self):
        GLib.timeout_add(500, self.on_timeout, None)
        update_mirrors()
        print(f"packages:{self.packages}")
        self.run_transaction()
        
