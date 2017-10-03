#!/bin/sh

# The Boss

sudo cp org.freedesktop.Anaconda.Boss.service /usr/share/dbus-1/system-services
sudo cp anaconda-boss.py /usr/sbin/anaconda-boss
sudo chmod o+x /usr/sbin/anaconda-boss
# Must match .service file?
sudo cp org.freedesktop.Anaconda.Boss.conf /usr/share/dbus-1/system.d
#sudo cp org.freedesktop.Anaconda.conf /etc/dbus-1/system.d

# Module: Timezone
sudo cp org.freedesktop.Anaconda.Module.Timezone.service /usr/share/dbus-1/system-services
sudo cp anaconda-module-timezone.py /usr/sbin/anaconda-module-timezone
sudo chmod o+x /usr/sbin/anaconda-module-timezone
sudo cp org.freedesktop.Anaconda.Module.Timezone.conf /usr/share/dbus-1/system.d

# Module: Storage
sudo cp org.freedesktop.Anaconda.Module.Storage.service /usr/share/dbus-1/system-services
sudo cp anaconda-module-storage.py /usr/sbin/anaconda-module-storage
sudo chmod o+x /usr/sbin/anaconda-module-storage
sudo cp org.freedesktop.Anaconda.Module.Storage.conf /usr/share/dbus-1/system.d

# Module: User
sudo cp org.freedesktop.Anaconda.Module.User.service /usr/share/dbus-1/system-services
# Test missing binary
#sudo cp anaconda-module-user.py /usr/sbin/anaconda-module-user
#sudo chmod o+x /usr/sbin/anaconda-module-user
sudo cp org.freedesktop.Anaconda.Module.User.conf /usr/share/dbus-1/system.d

# Module: Payload
sudo cp org.freedesktop.Anaconda.Module.Payload.service /usr/share/dbus-1/system-services
sudo cp anaconda-module-payload.py /usr/sbin/anaconda-module-payload
sudo chmod o+x /usr/sbin/anaconda-module-payload
# Test AccessDenied
#sudo cp org.freedesktop.Anaconda.Module.Payload.conf /usr/share/dbus-1/system.d 

# For addons, we want to run all we find

# Addon: Pony
sudo cp org.freedesktop.Anaconda.Addon.Pony.service /usr/share/dbus-1/system-services
sudo cp anaconda-addon-pony.py /usr/sbin/anaconda-addon-pony
sudo chmod o+x /usr/sbin/anaconda-addon-pony
sudo cp org.freedesktop.Anaconda.Addon.Pony.conf /usr/share/dbus-1/system.d

# Addon: Monitor
sudo cp org.freedesktop.Anaconda.Addon.Monitor.service /usr/share/dbus-1/system-services
sudo cp anaconda-addon-monitor.py /usr/sbin/anaconda-addon-monitor
sudo chmod o+x /usr/sbin/anaconda-addon-monitor
sudo cp org.freedesktop.Anaconda.Addon.Monitor.conf /usr/share/dbus-1/system.d

# systemd integration
# .service files are modified

sudo cp anaconda-module-timezone.service /usr/lib/systemd/system
sudo systemctl enable anaconda-module-timezone.service
sudo cp anaconda-module-storage.service /usr/lib/systemd/system
sudo systemctl enable anaconda-module-storage.service
sudo cp anaconda-addon-pony.service /usr/lib/systemd/system
sudo systemctl enable anaconda-addon-pony.service
sudo cp anaconda-addon-monitor.service /usr/lib/systemd/system
sudo systemctl enable anaconda-addon-monitor.service
sudo cp anaconda-module-payload.service /usr/lib/systemd/system
sudo systemctl enable anaconda-module-payload.service

sudo cp anaconda-boss.service /usr/lib/systemd/system
sudo systemctl enable anaconda-boss.service


