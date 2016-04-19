#!/usr/bin/python3

# https://www.freedesktop.org/wiki/Software/DBusBindings/ 
# using https://dbus.freedesktop.org/doc/dbus-python/

from gi.repository import GLib
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

# property decorator is only in F22 (added for server WG?). Not in F23.
# upstream:
# https://bugs.freedesktop.org/show_bug.cgi?id=26903#c14
# F22:
# http://pkgs.fedoraproject.org/cgit/rpms/dbus-python.git/commit/?id=b00d726b5b3e8f7f590ed3eb95160d1b68003339
#
# Python-dbus seems can have issues
# - may not be suitable due to type-guessing
# - threading problems with libdbus

class MyDBUSServiceF22(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.me.test', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/me/test')
        self._who = "human"
        self._state = "good"

    @dbus.service.method('org.me.test1')
    def hello(self):
        return "Hello %s!" % self._who

    @dbus.service.method('org.me.test1')
    def quit(self):
        GLib.MainLoop().quit()

    @dbus.service.method('org.me.test1.swear')
    def fuck_off(self):
        return "Fuck off, %s!" % self._who

    @dbus.service.property('org.me.test1', signature='s', emits_changed_signal=True)
    def Who(self):
        return self._who

    @Who.setter
    def Who(self, value):
        self._who = value

    @dbus.service.property('org.me.test1', signature='s', emits_changed_signal=True)
    def State(self):
        return self._state

# Introspection doesn't work for properties in F23

class Property():
    def __init__(self, value, writeable=False, signature="s"):
        self.value = value
        self.writeable = writeable
        self.signature = signature


class MyDBUSServiceF23(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.me.test', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/me/test')
        self.props = {}
        self.props["org.me.test1"] = {
                "Who" : Property("human", True, "s"),
                "State" : Property("good", False, "s"),
                }

    @dbus.service.method('org.me.test1')
    def hello(self):
        return "Hello %s!" % self.props["org.me.test1"]["Who"].value

    @dbus.service.method('org.me.test1')
    def quit(self):
        GLib.MainLoop().quit()
        return "Quitting!"

    @dbus.service.method('org.me.test1.swear')
    def fuck_off(self):
        return "Fuck off, %s!" % self.props["org.me.test1"]["Who"].value

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        if interface_name not in self.props:
            raise dbus.exceptions.DBusException('org.me.UnknownInterface',
                    'The test object does not implement the %s interface'
                    % interface_name)
        if property_name in self.props[interface_name]:
            return self.props[interface_name][property_name].value
        else:
            raise dbus.exceptions.DBusException('org.me.UnknownProperty',
                    'The %s interface does not have %s property'
                    % (interface_name, property_name))

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        if interface_name not in self.props:
            raise dbus.exceptions.DBusException('org.me.UnknownInterface',
                    'The test object does not implement the %s interface'
                    % interface_name)
        else:
            return {name: prop.value for name, prop in self.props[interface_name].items()}

    @dbus.service.method(dbus_interface=dbus.PROPERTIES_IFACE, in_signature='ssv')
    def Set(self, interface_name, property_name, new_value):
        if interface_name not in self.props:
            raise dbus.exceptions.DBusException('org.me.UnknownInterface',
                    'The test object does not implement the %s interface'
                    % interface_name)

        for name, prop in self.props[interface_name].items():
            if name == property_name:
                if prop.writeable:
                    prop.value = new_value
                else:
                    raise dbus.exceptions.DBusException('org.me.ReadOnlyProperty',
                            'The %s property is read-only' % property_name)
                break
        else:
            raise dbus.exceptions.DBusException('org.me.UnknownProperty',
                    'The %s interface does not have %s property'
                    % (interface_name, property_name))

        self.PropertiesChanged(interface_name, {property_name : new_value}, [])

    @dbus.service.signal(dbus_interface=dbus.PROPERTIES_IFACE,
            signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        pass

DBusGMainLoop(set_as_default=True)
#myservice = MyDBUSServiceF22()
myservice = MyDBUSServiceF23()
GLib.MainLoop().run()
