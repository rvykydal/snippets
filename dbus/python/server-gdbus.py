#!/usr/bin/python3

# https://www.freedesktop.org/wiki/Software/DBusBindings/
# using GDBus + PyGI
#
# Based on https://github.com/tasleson/py-gdbus-example-server
# requires Gio 2.46
# https://bugzilla.gnome.org/show_bug.cgi?id=656325

from gi.repository import Gio, GLib, GObject
import sys

loop = GObject.MainLoop()

introspection_xml =  \
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
            <method name='fuck_off'>
                <arg type='s' name='response' direction='out' />
            </method>
        </interface>
    </node>
"""

class MyDBUSService():
    def __init__(self):
        self._who = "human"
        self._state = "good"

    def handle_method_call(self, connection, sender, object_path, interface_name,
                           method_name, parameters, invocation):
        if interface_name == "org.me.test1":
            if method_name == "hello":
                ret = GLib.Variant("s", "Hello '%s!'" % self._who)
                t = GLib.Variant.new_tuple(ret)
                invocation.return_value(t)
            elif method_name == "quit":
                loop.quit()

        elif interface_name == "org.me.test1.swear":
            if method_name == "fuck_off":
                ret = GLib.Variant("s", "Fuck off '%s!'" % self._who)
                t = GLib.Variant.new_tuple(ret)
                invocation.return_value(t)

        return None

    def handle_get_property(self, connection, sender, object_path, interface_name, value):

        ret = None
        if interface_name == "org.me.test1":
            if value == 'Who':
                ret = GLib.Variant("s", self._who)
            elif value == 'State':
                ret = GLib.Variant("s", self._state)
        return ret

    def handle_set_property(self, connection, sender, object_path, interface_name, key,
                            value):

        if interface_name == "org.me.test1":
            if key == 'Who':
                self._who = str(value)

            p1 = GLib.Variant('s', str(interface_name))
            p2 = GLib.Variant('a{sv}',
                            {'Who': GLib.Variant('s', self._who)})
            p3 = GLib.Variant('as', ())
            values = GLib.Variant.new_tuple(p1, p2, p3)

            Gio.DBusConnection.emit_signal(
                connection,
                None,
                object_path,
                "org.freedesktop.DBus.Properties",
                "PropertiesChanged",
                values
            )

        # What is the correct thing to return here on success?  It appears that
        # we need to return something other than None or what would be evaluated
        # to False for this call back to be successful.
        return True


def on_bus_acquired(connection, name, *args):
    service = MyDBUSService()
    for interface in introspection_data.interfaces:
        reg_id = Gio.DBusConnection.register_object(
            connection,
            "/org/me/test",
            interface,
            service.handle_method_call,
            service.handle_get_property,
            service.handle_set_property)

        if reg_id == 0:
            print('Error while registering object!')
            sys.exit(1)

def on_name_acquired(connection, name, *args):
    pass

def on_name_lost(connection, name, *args):
    sys.exit(1)

introspection_data = Gio.DBusNodeInfo.new_for_xml(introspection_xml)

owner_id = Gio.bus_own_name(Gio.BusType.SESSION,
                            "org.me.test",
                            Gio.BusNameOwnerFlags.NONE,
                            on_bus_acquired,
                            on_name_acquired,
                            on_name_lost
                            )

loop.run()

Gio.bus_unown_name(owner_id)
