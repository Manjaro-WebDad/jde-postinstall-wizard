import gi
gi.require_version('Pamac', '10.0')
from sources import load_yaml
from utils import progressbar
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
 
    def get_app_icon(self, pkg):
        return self.db.get_pkg(pkg).get_icon()

    def get_app_name(self, pkg):
        return self.db.get_pkg(pkg).get_app_name()

    def test_pkg(self, pkg):
        return self.db.get_pkg(pkg).get_name()

    def on_emit_action(self, transaction, action, data):
       print(action)

    def on_emit_action_progress(self, transaction, action, status, progress, data):
        print(f"{action} {status} {progress}")
        progressbar.set_fraction(progress)
      

    def on_emit_hook_progress(self, transaction, action, details, status, progress, data):
        print(f"{action} {details} {status}")

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
       print(self.packages)
       progressbar.pulse()
       for pkg in self.packages:
         self.transaction.add_pkg_to_install(pkg)

       self.transaction.run_async(self.on_transaction_finished_callback, None)
       self.loop.run()

    def install(self):
        self.run_transaction()
        
