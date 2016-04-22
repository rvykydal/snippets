#!/usr/bin/python3

# https://www.freedesktop.org/wiki/Software/DBusBindings/
# using https://github.com/LEW21/pydbus

# requires Gio 2.46
# https://bugzilla.gnome.org/show_bug.cgi?id=656325

from gi.repository import GObject
from pydbus import SessionBus
from pydbus.generic import signal

loop = GObject.MainLoop()

class MyDBUSService(object):
    """
        <node>
            <interface name='org.me.test1'>
                <method name='hello'>
                    <arg type='s' name='response' direction='out' />
                </method>
                <method name='quit' />
                <property name='Who' type='s' access='readwrite'>
                    <annotation name='org.freedesktop.DBus.Property.EmitsChangedSignal' value='true'/>
                </property>
                <property name='State' type='s' access='read'>
                    <annotation name='org.freedesktop.DBus.Property.EmitsChangedSignal' value='true'/>
                </property>
            </interface>
            <interface name='org.me.test1.swear'>
                <method name='whatsup'>
                    <arg type='s' name='response' direction='out' />
                </method>
            </interface>
        </node>
    """

    def __init__(self):
        self._who = "human"
        self._state = "good"

    def hello(self):
        return "Hello %s!" % self._who

    def quit(self):
        loop.quit()

    def whatsup(self):
        return "@!#$*&@!, %s!" % self._who

    @property
    def State(self):
        return self._state

    @property
    def Who(self):
        return self._who

    @Who.setter
    def Who(self, value):
        self._who = value
        self.PropertiesChanged("org.me.test1", {"Who": self._who}, [])

    PropertiesChanged = signal()

bus = SessionBus()
bus.publish("org.me.test", MyDBUSService())
loop.run()
