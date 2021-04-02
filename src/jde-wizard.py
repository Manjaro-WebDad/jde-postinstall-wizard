#!/usr/bin/env python
# Copyright (C) 2021 Vitor Lopes

import gi
import os
from gi.repository import Gtk, Gdk, GdkPixbuf
gi.require_version("Gtk", "3.0")
from sources import get_remote_source, load_yaml
from packageManager import Pamac  
from utils import progressbar
pamac = Pamac()

class Wizard:
    def __init__(self):
        self.last_page = 0
        self.wizard = Gtk.Assistant()
        self.wizard.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)
        self.wizard.fullscreen()
        self.wizard.set_title("Wizard")
        self.wizard.connect('cancel', self.on_close_cancel)
        self.wizard.commit()
        self.wizard.connect('close', self.on_close_cancel)
        self.wizard.connect('prepare', self.on_prepare)
        self.pre_selected = pamac.data.get("pre-selected")
        self.intro()
        self.pages()    
        self.wizard.show()  
        

    def on_close_cancel(self, wizard):
        wizard.destroy()
        Gtk.main_quit()

    def on_apply(self, wizard, label):
        label.set_text("Installing, grab a cup of coffee")
        try:
            lock = "/var/lib/pacman/db.lck"
            if os.path.isfile(lock):
                ##TODO show warning modal
                pass
            else:
                f = open(lock, "w")
                f.close()
                os.remove(lock)
                ##TODO show reboot modal
        except PermissionError:
            pass
        finally:
            pamac.install()            

    def on_prepare(self, wizard, page):
        current_page = self.wizard.get_current_page()
        print(f"page:{current_page} {pamac.packages}")
        if current_page == 0:
            pamac.check_packages( pamac.data.get("base") )
        
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
        pamac.check_packages( user_data.get("packages") )

    def app_on_select(self, btn, pkg):
        if btn.get_active():
            pamac.check_packages(pkg)
        else:
            try:
                pamac.packages.remove(pkg)
            except ValueError:
                pass
        print(pamac.packages)


    def intro(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_column_spacing(10)
        grid.set_column_homogeneous(True)
        grid.props.valign = grid.props.halign = Gtk.Align.CENTER
        self.wizard.add(grid)
        label1 = Gtk.Label()
        label1.set_markup(
            "Hi, lets personalize and finish installation."
        )
        label2 = Gtk.Label(
            label="Make sure you are connected to the internet before proceding."
        )
        
        label2.set_line_wrap(True)
        label2.get_style_context().add_class("margin-bottom")
        label1.set_max_width_chars(32)
        entry = Gtk.Entry()
        entry.set_text("optional: insert a remote software workflow in yaml format")
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
            box = Gtk.VBox(spacing=12)
            box.props.valign = Gtk.Align.CENTER
            box.props.halign = Gtk.Align.CENTER
            box.set_border_width(12)
            grid = Gtk.Grid()
            grid.get_style_context().add_class("apps")
            box.add(grid)
            label = Gtk.Label(label=title)
            grid.attach(label, 0, 0, 1, 1)
            label.get_style_context().add_class("category")
            next_row = 1           

            for pkg in pkg_list:                
                next_row += 1
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=pamac.get_app_icon(pkg),
                        width=32,
                        height=32,
                        preserve_aspect_ratio=True
                        )
                    icon = Gtk.Image.new_from_pixbuf(pixbuf)
                    checkbutton = Gtk.CheckButton(label=pamac.get_app_name(pkg))
                    checkbutton.connect("toggled", self.app_on_select, pkg)
                    grid.attach(checkbutton, 0, next_row, 1, 1)
                    grid.attach_next_to(icon, checkbutton, Gtk.PositionType.RIGHT, 2, 1) 
                    if pkg in self.pre_selected:
                        checkbutton.set_active(True)
                except AttributeError:
                    print("package does not exits")

            box.show_all()
            self.wizard.append_page(box)
            self.wizard.set_page_complete(box, True)
            self.wizard.set_page_title(box, title)
            self.wizard.set_page_type(box, Gtk.AssistantPageType.PROGRESS)

    def done_page(self):
        box = Gtk.HBox(spacing=12)
        box.set_border_width(12)        
        grid = Gtk.Grid()
        label = Gtk.Label(
            label='All setup, press apply to continue'
            )
        label.set_hexpand(True)
        box.pack_start(grid, True, True, 0)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(progressbar, 0, 2, 1, 1)
        grid.set_row_spacing(20)
        grid.set_baseline_row(2)
        grid.set_row_homogeneous(True)
        grid.props.valign = grid.props.halign = Gtk.Align.CENTER
        box.show_all()
        self.wizard.connect('apply', self.on_apply, label)
        self.wizard.append_page(box)
        self.wizard.set_page_complete(box, True)
        self.wizard.set_page_title(box, 'All Done')
        self.wizard.set_page_type(box, Gtk.AssistantPageType.CONFIRM)
        
    provider = Gtk.CssProvider()
    css = b"""
        box grid label {
            color: white;
            font-size: 20px;
            font-weight:bold;
            }
            
        progress, trough {
            min-height: 1px;
        }
        
        progressbar > trough > progress {
            background-image: none;
            background-color: #e91e63;
            }
            
        .sidebar label {
            color:red;
            font-size:0;
            opacity:0;
            }
            
        .sidebar {
            border:0;
            }
            
        box .apps label:not(.category) {
            font-size:16px;
            color: white;
            font-weight:bold;
            padding:10px;
            }
            
        box {
            background:#4a148c;
            }
            
        entry {
            padding:8px;
            }
            
        .margin-bottom {
            border-bottom: 40px solid transparent;
            }
            
        label.category {
            border-bottom: 40px solid transparent;
            font-size: 32px;
            }
            
        button:first-child {
            color:white;
            background:#f44336;
            }
            
        button:last-child {
            color:white;
            background:#009688;
            }
            
        check {
            min-height: 20px;
            min-width: 20px;
        }
        """

    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                                             provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

   
def main():
    Wizard()
    Gtk.main()


if __name__ == '__main__':
    main()
