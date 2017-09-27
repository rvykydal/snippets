#!/bin/sh

dbus-send --system --print-reply \
	--dest=org.freedesktop.DBus \
	/org/freedesktop/DBus \
	org.freedesktop.DBus.StartServiceByName \
	string:org.freedesktop.Anaconda.Boss uint32:0

