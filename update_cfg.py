#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, var, shutil
from PyQt4 import QtGui
from multibootusb_ui import Ui_Dialog


class AppGui(QtGui.QDialog, Ui_Dialog):
    def update_distro_cfg_files(self, distro, iso_name, iso_cfg_ext_dir):
        #print "Updating config files..."
        self.ui.status.setText("Updating config files...")
        QtGui.qApp.processEvents()
        for dirpath, dirnames, filenames in os.walk(iso_cfg_ext_dir):
            for f in filenames:
                if f.endswith(".cfg"):
                    cfg_file = os.path.join(dirpath, f)
                    try:
                        string = open(cfg_file).read()
                    except IOError:
                        print "Unable to read " + cfg_file
                    else:
                        replace_text = r'\1/multibootusb/' + os.path.splitext(iso_name)[0] + '/'
                    #string = re.sub(r'(append) (\S+)', r'\2\n    \1', re.sub(r'([ \t =,])/', replace_text, string))
                    string = re.sub(r'([ \t =,])/', replace_text, string)
                    if distro == "ubuntu":
                        #string = re.sub(r'file=/cdrom/', 'file=/cdrom/multibootusb/' + os.path.splitext(iso_name)[0] + '/',  string)
                        string = re.sub(r'boot=casper',
                                        'boot=casper cdrom-detect/try-usb=true floppy.allowed_drive_mask=0 ignore_uuid ignore_bootid root=UUID=' + str(
                                            var.gbl_usb_uuid) + ' live-media-path=/multibootusb/' +
                                        os.path.splitext(iso_name)[0] + '/casper', string)
                    elif distro == "debian":
                        string = re.sub(r'boot=live', 'boot=live ignore_bootid live-media-path=/multibootusb/' +
                                                      os.path.splitext(iso_name)[0] + '/live', string)
                    elif distro == "fedora":
                        string = re.sub(r'root=\S*', 'root=UUID=' + str(var.gbl_usb_uuid) + ' live_dir=/multibootusb/' +
                                                     os.path.splitext(iso_name)[0] + '/LiveOS', string)
                    elif distro == "parted-magic":
                        string = re.sub(r'initrd=',
                                        'directory=/multibootusb/' + os.path.splitext(iso_name)[0] + '/ initrd=',
                                        string)
                    elif distro == "ubcd":
                        string = re.sub(r'iso_filename=\S*', 'directory=/multibootusb/' + os.path.splitext(iso_name)[0],
                                        string, flags=re.I)
                    elif distro == "ipcop":
                        string = re.sub(r'ipcopboot=cdrom\S*', 'ipcopboot=usb', string)
                    elif distro == "puppy":
                        string = re.sub(r'pmedia=cd\S*',
                                        'pmedia=usbflash psubok=TRUE psubdir=/multibootusb/' + os.path.splitext(iso_name)[0] + '/',
                                        string)
                    elif distro == "slax":
                        string = re.sub(r'initrd=', '\1 from=/multibootusb/' + os.path.splitext(iso_name)[
                            0] + '/slax fromusb initrd=', string)
                    elif distro == "knoppix":
                        string = re.sub(r'append',
                                        '\1  knoppix_dir=/multibootusb/' + os.path.splitext(iso_name)[0] + '/KNOPPIX',
                                        string)
                    elif distro == "systemrescuecd":
                        string = re.sub(r'append', '\1 subdir=/multibootusb/' + os.path.splitext(iso_name)[0] + '/',
                                        string, flags=re.I)
                    elif distro == "arch" or distro == "chakra":
                        string = re.sub(r'isolabel=\S*', 'isodevice=/dev/disk/by-uuid/' + str(var.gbl_usb_uuid), string,
                                        flags=re.I)
                        string = re.sub(r'isobasedir=',
                                        'isobasedir=/multibootusb/' + os.path.splitext(iso_name)[0] + '/', string,
                                        flags=re.I)
                    elif distro == "suse" or distro == "opensuse":
                        if re.search(r'opensuse_12', string, re.I):
                            string = re.sub(r'append', 'append loader=syslinux isofrom=/dev/disk/by-uuid/' + str(
                                var.gbl_usb_uuid) + ":/" + str(iso_name), string, flags=re.I)
                        else:
                            string = re.sub(r'append', 'append loader=syslinux isofrom_device=/dev/disk/by-uuid/' + str(
                                var.gbl_usb_uuid) + ' isofrom_system=/' + str(iso_name), string, flags=re.I)
                    elif distro == "pclinuxos":
                        string = re.sub(r'livecd=',
                                        'fromusb livecd=' + '/multibootusb/' + os.path.splitext(iso_name)[0] + '/',
                                        string)
                    elif distro == "porteus" or distro == "wifislax":
                        string = re.sub(r'initrd=',
                                        'from=' + '/multibootusb/' + os.path.splitext(iso_name)[0] + ' initrd=', string)
                    elif distro == "hbcd":
                        string = re.sub(r'/HBCD', '/multibootusb/' + os.path.splitext(iso_name)[0] + '/HBCD', string)
                    elif distro == "zenwalk":
                        string = re.sub(r'initrd=', 'from=/multibootusb/' + os.path.splitext(iso_name)[
                            0] + '/' + iso_name + ' initrd=', string)
                    elif distro == "mageialive":
                        string = re.sub(r'LABEL=\S*', 'LABEL=' + var.usb_label, string)
                    elif distro == "antix":
                        string = re.sub(r'APPEND', 'image_dir=/multibootusb/' + os.path.splitext(iso_name)[0], string)
                    elif distro == "solydx":
                        string = re.sub(r'live-media-path=', 'live-media-path=/multibootusb/' + os.path.splitext(iso_name)[0], string)
                    elif distro == "salix-live":
                        string = re.sub(r'iso_path', '/multibootusb/' + os.path.splitext(iso_name)[0] + '/' + iso_name, string)

                    config_file = open(cfg_file, "wb")
                    config_file.write(string)
                    config_file.close()

        self.update_syslinux_cfg_file(iso_cfg_ext_dir, iso_name, var.gbl_sys_cfg_file)

    def update_syslinux_cfg_file(self, iso_cfg_ext_dir, iso_name, sys_cfg_file):
        usb_mount_count = len(str(self.ui.usb_mount.text()[9:]))
        isolinux_path = None
        print "Updating config files..."
        self.ui.status.setText("Updating config files...")
        QtGui.qApp.processEvents()
        if os.path.exists(sys_cfg_file):

            if var.distro == "hbcd":
                if os.path.exists(var.usb_mount + "multibootusb", "menu.lst"):
                    config_file = open(os.path.exists(var.usb_mount + "multibootusb", "menu.lst"), "wb")
                    string = re.sub(r'/HBCD', '/multibootusb/' + os.path.splitext(iso_name)[0] + '/HBCD', string)
                    config_file.write(string)
                    config_file.close()

            if var.distro == "windows":
                if os.path.exists(sys_cfg_file):
                    config_file = open(sys_cfg_file, "a")
                    config_file.write("#start windows" + "\n")
                    config_file.write("LABEL windows" + "\n")
                    config_file.write("MENU LABEL windows" + "\n")
                    #config_file .write("CONFIG /" + isolinux_path.replace("\\", "/") + "\n")
                    config_file.write("KERNEL chain.c32 hd0 1 ntldr=/bootmgr" + "\n")
                    config_file.write("#end windows" + "\n")
                    config_file.close()

            else:
                config_file = open(sys_cfg_file, "a")
                config_file.write("#start " + os.path.splitext(iso_name)[0] + "\n")
                config_file.write("LABEL " + os.path.splitext(iso_name)[0] + "\n")
                config_file.write("MENU LABEL " + os.path.splitext(iso_name)[0] + "\n")
                if var.distro == "salix-live":
                    config_file.write(
                        "LINUX " + '/multibootusb/' + os.path.splitext(iso_name)[0] + '/boot/grub2-linux.img' + "\n")
                elif var.distro == "pclinuxos":
                    config_file.write("kernel " + '/multibootusb/' + os.path.splitext(iso_name)[0] + '/isolinux/vmlinuz' + "\n")
                    config_file.write("append livecd=livecd root=/dev/rd/3 acpi=on vga=788 keyb=us vmalloc=256M nokmsboot fromusb root=UUID=" + var.gbl_usb_uuid + " bootfromiso=/multibootusb/" + os.path.splitext(iso_name)[0] + "/" + iso_name + " initrd=/multibootusb/" + os.path.splitext(iso_name)[0] + '/isolinux/initrd.gz' + "\n")
                else:
                    config_file.write("BOOT " + var.distro_sys_install_bs[usb_mount_count:].replace("\\", "/") + "\n")
                config_file.write("#end " + os.path.splitext(iso_name)[0] + "\n")
                config_file.close()

        for dirpath, dirnames, filenames in os.walk(iso_cfg_ext_dir):
            for f in filenames:
                if f.endswith("isolinux.cfg"):
                    shutil.copy2(os.path.join(dirpath, f), os.path.join(dirpath, "syslinux.cfg"))
