Install
-------

  ./install.sh

Installs

- dbus services
- dbus service configuration files
- systemd service unit files

Enables systemd servies to create dbus-* alias symlinks.

Run
---

Run the Boss:

  ./run.sh

Watch logs in ``/tmp/anaconda.log``.
Watch services with d-feet.

- Modules to start defined in Boss. Look at the code, there are also some modules that should fail in various ways.
- (Installed) addons are discovered by ListActivatableNames DBus method.
- Modules and addons are started by asynchronous calls to StartServiceByName DBus method.
- When all required modules and found addons are started, Boss tells them.

Or you can run it by

  sudo systemctl start anaconda-boss.service

Stop
----

Stop the Boss

  ./stop.sh

or call ``org.freedesktop.Anaconda.Boss.Quit()`` which should quit also modules.

Stopping anaconda-boss.service by systemctl does not work as module services are left running orphaned.

Uninstall
---------

  ./uninstall.sh

Uninstall

- dbus services
- its configuration files (.service, .conf)
- dbus-* symlinks to systemd services
