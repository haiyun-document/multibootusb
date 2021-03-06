#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,  re,  var,  psutil,  threading,  shutil
from PyQt4 import QtGui
from multibootusb_ui import Ui_Dialog

uninstall_distro_name = ""
class AppGui(QtGui.QDialog,Ui_Dialog):
    def uninstall_distro(self):
        global uninstall_distro_name
        if self.ui.listWidget.currentItem() == None:
            print "Please select a distro from the list."
            QtGui.QMessageBox.information(self, 'No selection.', 'Please select a distro from the list.')
        else:
            uninstall_distro_name = str(self.ui.listWidget.currentItem().text())
            sys_cfg_file = os.path.join(str(var.usb_mount),  "multibootusb",  "syslinux.cfg")
            print sys_cfg_file
            
            if not os.path.exists(str(var.usb_mount) + "/multibootusb/" +  uninstall_distro_name.strip()):
                print "Distro install directory not found."
                QtGui.QMessageBox.information(self, 'No install directory.', 'Distro install directory is not found.\nPlease remove the entry from syslinux.cfg file manually.')
            else:
                reply = QtGui.QMessageBox.question(self, "Review selection...",
                                       "Are you sure to uninstall " +  uninstall_distro_name,
                                      QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
                    
                if reply == QtGui.QMessageBox.Yes:
                    self.ui.status.setText("Uninstalling " + uninstall_distro_name)
                    inintial_usb_size = int(psutil.disk_usage(var.usb_mount)[1])
                    
                    var.distro_uninstall = self.detect_iso(str(var.usb_mount) + "/multibootusb/" +  uninstall_distro_name.strip())
                    
                    if var.distro_uninstall == "opensuse":
                        folder_size_to_remove = os.path.getsize(os.path.join(var.usb_mount, uninstall_distro_name.strip()) + ".iso")
                        folder_size_to_remove += self.get_size(str(var.usb_mount) + "/multibootusb/" +  uninstall_distro_name.strip())
                    elif uninstall_distro_name.strip() == "windows":
                        var.distro_uninstall = "windows"
                        folder_size_to_remove = self.get_size(str(var.usb_mount) + "/SOURCES")
                    elif var.distro_uninstall == "ipfire":
                        folder_size_to_remove = self.get_size(str(var.usb_mount) + "/multibootusb/" +  uninstall_distro_name.strip())
                        files = os.listdir(os.path.join(str(var.usb_mount)))
                        for f in files:
                            if f.endswith('.tlz'):
                                folder_size_to_remove += os.path.getsize(os.path.join(str(var.usb_mount), f))
                    else:
                        
                        folder_size_to_remove = self.get_size(str(var.usb_mount) + "/multibootusb/" +  uninstall_distro_name.strip())
                    print folder_size_to_remove
                    
                    thrd = threading.Thread(target=self.remove_dir, name="")
                    thrd.start()
                    while thrd.is_alive():
                        current_size = int(psutil.disk_usage(var.usb_mount)[1])
                        diff_size = int(inintial_usb_size - current_size)
                        percentage = float(diff_size)/folder_size_to_remove*100
                        self.ui.progressBar.setValue(percentage)
                        QtGui.qApp.processEvents()
                    print ("Distro uninstall Complete..")
                    self.ui.progressBar.setValue(100)
                    self.ui.progressBar.setValue(0)
                    self.ui.status.clear()
                        
                    print "Updating syslinux.cfg file..."
                    string = open(sys_cfg_file).read()
                    string = re.sub(r'#start ' + uninstall_distro_name.strip() + '.*?' + '#end ' + uninstall_distro_name.strip() + '\s*', '',  string, flags=re.DOTALL)
                    config_file = open(sys_cfg_file, "w")
                    config_file .write(string)
                    config_file .close()
                    self.update_list_box(sys_cfg_file)
                    self.onComboChange()
                    QtGui.QMessageBox.information(self, 'Uninstall...',  uninstall_distro_name.strip() + ' ' + 'is successfully removed.')
                    
    def remove_dir(self):
        global uninstall_distro_name
        for path, subdirs, files in os.walk((os.path.join(str(var.usb_mount), "multibootusb", uninstall_distro_name.strip()))):
            for name in files:
                if name.endswith('ldlinux.sys'):
                    os.chmod(os.path.join(path, name), 0777)
                    os.unlink(os.path.join(path, name))
        if var.distro_uninstall == "opensuse":
            os.remove (os.path.join(str(var.usb_mount), uninstall_distro_name.strip() + ".iso"))
        elif var.distro_uninstall == "windows":
            windows_files = ["SOURCES","BOOT","[BOOT]","EFI","SUPPORT","UPGRADE","AUTORUN.INF","BOOTMGR","README.TXT","SETUP.EXE"]
            for f in window_files:
                if os.path.isfile(os.path.join(str(var.usb_mount), f)):
                    os.remove(os.path.join(str(var.usb_mount), f))
                elif os.path.isdir(os.path.join(str(var.usb_mount), f)):
                    shutil.rmtree(os.path.join(str(var.usb_mount), f))

        if var.distro_uninstall == "ipfire":
            files = os.listdir(str(var.usb_mount))
            for f in files:
                if f.endswith('.tlz'):
                    os.remove(os.path.join(str(var.usb_mount), f))
        if os.path.exists(os.path.join(str(var.usb_mount), "multibootusb", uninstall_distro_name.strip())):
            shutil.rmtree (os.path.join(str(var.usb_mount), "multibootusb", uninstall_distro_name.strip()))
        var.distro_uninstall = ""
