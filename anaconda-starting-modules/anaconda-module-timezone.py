#!/usr/bin/python3

from gi.repository import GLib, Gio
from pydbus import SystemBus
from pydbus.generic import signal
from pydbus.error import register_error
import time
import random

loop = GLib.MainLoop()

import logging
logging.basicConfig(filename='/tmp/anaconda.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


DOMAIN = Gio.DBusError.quark() # TODO: Register new domain.

@register_error("org.freedesktop.Anaconda.Module.Error.InvalidPropertyValue", DOMAIN, 1000)
class InvalidPropertyValueError(Exception):
    pass

class Timezone(object):
    """
        <node>
            <interface name='org.freedesktop.Anaconda.Module.Timezone'>
                <method name='EchoString'>
                    <arg type='s' name='question' direction='in'/>
                    <arg type='s' name='response' direction='out'/>
                </method>
                <method name='Quit'/>
                <method name='setTimezoneSpec'>
                    <arg type='s' name='timezone specification' direction='in'/>
                </method>
                <property name="TimezoneSpec" type="s" access="readwrite">
                    <annotation name="org.freedesktop.DBus.Property.EmitsChangedSignal" value="true"/>
                </property>
            </interface>
        </node>
    """

    def __init__(self):
        self._TimezoneSpec = "tz_1"

    @property
    def TimezoneSpec(self):
        return self._TimezoneSpec

    @TimezoneSpec.setter
    def TimezoneSpec(self, value):
        if not value.startswith("tz"):
            logging.debug("%s: TimezoneSpec setter: invalid value: %s" % (self.__class__.__name__, value))
            msg = "Invalid TimezoneSpec value %s" % value
            raise InvalidPropertyValueError(msg)
        else:
            self._TimezoneSpec = value
            logging.debug("%s: TimezoneSpec setter: value set: %s" % (self.__class__.__name__, value))
            self.PropertiesChanged("org.freedesktop.Anaconda.Module.Timezone", {"TimezoneSpec": self.TimezoneSpec}, [])

    def setTimezoneSpec(self, value):
        if not value.startswith("tz"):
            logging.debug("%s: setTimezoneSpec: invalid value: %s" % (self.__class__.__name__, value))
            msg = "Invalid TimezoneSpec value %s" % value
            raise InvalidPropertyValueError(msg)
        else:
            self._TimezoneSpec = value
            logging.debug("%s: setTimezoneSpec: value set: %s" % (self.__class__.__name__, value))
            self.PropertiesChanged("org.freedesktop.Anaconda.Module.Timezone", {"TimezoneSpec": self.TimezoneSpec}, [])

    PropertiesChanged = signal()

    def EchoString(self, s):
        """returns whatever is passed to it"""
        logging.debug("%s: EchoString %s" % (self.__class__.__name__, s))
        return s

    def Quit(self):
        """removes the object from the DBUS connection and exits"""
        logging.debug("%s: Quit" % self.__class__.__name__)
        GLib.timeout_add_seconds(1, loop.quit)

    def initialize(self):
        """initialize boss before publishing"""
        logging.debug("%s: intialize started" % self.__class__.__name__)
        #time.sleep(random.randrange(4))
        logging.debug("%s: intialize finished" % self.__class__.__name__)

bus = SystemBus()
module = Timezone()
module.initialize()
bus.publish("org.freedesktop.Anaconda.Module.Timezone", module)
loop.run()
