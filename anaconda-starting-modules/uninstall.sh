#!/bin/sh

sudo rm /usr/sbin/anaconda-module-*
sudo rm /usr/sbin/anaconda-addon-*
sudo rm /usr/sbin/anaconda-boss

sudo rm /usr/share/dbus-1/system-services/org.freedesktop.Anaconda.*.service
sudo rm /usr/share/dbus-1/system.d/org.freedesktop.Anaconda.*.conf

