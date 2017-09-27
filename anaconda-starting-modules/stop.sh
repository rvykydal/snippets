#!/bin/sh

dbus-send --system --print-reply \
	--dest=org.freedesktop.Anaconda.Boss \
	/org/freedesktop/Anaconda/Boss \
	org.freedesktop.Anaconda.Boss.Quit
