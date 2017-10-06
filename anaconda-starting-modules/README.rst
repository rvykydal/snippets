Install
-------

  ./install.sh

Installs

- dbus services
- dbus service configuration files
- systemd service unit files of modules and addons
- anaconda-modules.target systemd unit to run module/addon systemd services

Enables modules systemd servies to create dbus-* alias symlinks and add the service to .wants of anaconda-modules.target

Run
---

Run the Boss:

  sudo systemctl start anaconda-boss.service

Watch logs in ``/tmp/anaconda.log``.
Watch services with d-feet.

- Modules/addons which will be started are defined by installing module/addon systemd service (wanted by anaconda-modules.target)
- Boss watches module services appearing on system bus with NameOwnerChanged signal.
- Modules required by Boss are defined in Boss (do not require failing modules, eg Payload as they are not worked out).
- When all required modules and found addons are started, Boss tells them.

Stop
----

Stop the Boss

  ./stop.sh

or call ``org.freedesktop.Anaconda.Boss.Quit()`` which should quit also modules.

Stopping anaconda-boss.service by systemctl does not work, module services are left running orphaned.

To clean up also run:

  sudo systemctl stop anaconda-modules.target

Uninstall
---------

  ./uninstall.sh

Uninstalls

- dbus services
- its configuration files (.service, .conf)
- dbus-* symlinks to systemd services
- anaconda-modules.target
