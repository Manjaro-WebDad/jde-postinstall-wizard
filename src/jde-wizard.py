#!/usr/bin/env python
# Copyright (C) 2021 Vitor Lopes

import gi
from gi.repository import Gtk
gi.require_version("Gtk", "3.0")
from sources import get_remote_source, load_yaml
from packageManager import Pamac  
from utils import progressbar
pamac = Pamac()

class Wizard:
    def __init__(self):
        self.last_page = 0
        self.wizard = Gtk.Assistant(use_header_bar=True)
        self.wizard.set_default_size(800, 600)
        self.wizard.set_title("Wizard")
        self.wizard.connect('cancel', self.on_close_cancel)
        self.wizard.connect('close', self.on_close_cancel)
        self.wizard.connect('apply', self.on_apply)
        self.wizard.connect('prepare', self.on_prepare)
        self.intro()
        self.pages()    
        self.wizard.show()        

    def on_close_cancel(self, wizard):
        wizard.destroy()
        Gtk.main_quit()

    def on_apply(self, wizard):
        pamac.install()

    def on_prepare(self, wizard, page):
        current_page = self.wizard.get_current_page()
        print(f"page:{current_page} {pamac.packages}")
        if current_page == 0:
            packages = pamac.data.get("base")
            if packages != None:
                for pkg in packages:
                    if pamac.test_pkg(pkg) == pkg:
                        pamac.packages.append(pkg)
        
        elif current_page == self.last_page:
            self.done_page()

    def on_input_changed(self, *args):
        input = args[0].get_text()
        user_data = load_yaml(
            source=get_remote_source(
                source=input
                )
            )
        ##TODO: this section needs to be added at the end in case packages already exist in the list
        packages = user_data.get("packages")
        for pkg in packages:
            pamac.packages.append(pkg)

    def app_on_select(self, btn, pkg):
        if btn.get_active():
            pamac.packages.append(pkg)
        else:
            pamac.packages.remove(pkg)
        print(pamac.packages)


    def intro(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_column_spacing(10)
        grid.set_column_homogeneous(True)
        self.wizard.add(grid)
        label1 = Gtk.Label()
        label1.set_markup(
            "Hi welcome, lets finish your installation."
        )
        label2 = Gtk.Label(
            label="Make sure you are connected to the internet before proceding."
        )
        
        label2.set_line_wrap(True)
        label1.set_max_width_chars(32)
        entry = Gtk.Entry()
        entry.set_text("remote software workflow in yaml format")
        grid.attach(label1, 0, 0, 1, 1)
        grid.attach(label2, 0, 2, 1, 1)
        grid.attach(entry, 0, 3, 1, 1)
        grid.show_all()
        self.wizard.append_page(grid)
        self.wizard.set_page_complete(grid, True)
        self.wizard.set_page_title(grid, 'Remote Workflow')
        self.wizard.set_page_type(grid, Gtk.AssistantPageType.PROGRESS)
        entry.connect("changed", self.on_input_changed)

    def pages(self):      
        software = pamac.data.get("software")

        for p in software:
            self.last_page += 1
            title = p["group"][0]["category"]
            pkg_list = p["group"][1]["packages"]
            box = Gtk.VBox(homogeneous=False, spacing=12)
            box.set_border_width(12)
            grid = Gtk.Grid()
            box.add(grid)
            next_row = 0           

            for pkg in pkg_list:                
                grid.set_row_homogeneous(False)
                grid.set_column_homogeneous(False)
                next_row += 1
                try:
                    image = Gtk.Image.new_from_file(pamac.get_app_icon(pkg))
                    checkbutton = Gtk.CheckButton(label=pamac.get_app_name(pkg))
                    checkbutton.connect("toggled", self.app_on_select, pkg)
                    grid.attach(checkbutton, 0, next_row, 1, 1)
                    grid.attach_next_to(image, checkbutton, Gtk.PositionType.RIGHT, 2, 1)                    
                except AttributeError:
                    print("package does not exits")

            box.show_all()
            self.wizard.append_page(box)
            self.wizard.set_page_complete(box, True)
            self.wizard.set_page_title(box, title)
            self.wizard.set_page_type(box, Gtk.AssistantPageType.PROGRESS)

    def done_page(self):
        box = Gtk.HBox(homogeneous=False, spacing=12)
        box.set_border_width(12)        
        grid = Gtk.Grid()
        label = Gtk.Label(
            label='This is a confirmation page, press apply if you ready'
            )
        label.set_hexpand(True)
        box.pack_start(grid, True, True, 0)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(progressbar, 0, 2, 1, 1)
        grid.set_row_spacing(20)
        grid.set_baseline_row(2)
        box.show_all()
        self.wizard.append_page(box)
        self.wizard.set_page_complete(box, True)
        self.wizard.set_page_title(box, 'All Done')
        self.wizard.set_page_type(box, Gtk.AssistantPageType.CONFIRM)

   
def main():
    Wizard()
    Gtk.main()


if __name__ == '__main__':
    main()
