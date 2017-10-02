#!/usr/bin/python3

# questions
# - do we want modules / addons to be systemd services
#   - starting via systemd units (.wants of modules / addon .target created during
#     installation)
#   - (-) acivation error reports
#   - (-) harder synchronization (based on dbus names API)
#   - (+/-) boss doesn't have complete control over module lifecycle,
#         synchronization via systemd
#   - hybrid solution - starting systemd service via dbus
#   - we still may want module reload handling by boss (based on dbus names API)
# - do we want to be able to restart boss while keeping modules alive?
#
# - explicitly start services vs watching names:
#   (+/-) explicit start has a timeout?

from gi.repository import GLib, Gio
from pydbus import SystemBus
from pydbus.error import register_error
import time
import random
import os

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

ANACONDA_ADDON_SERVICE_PREFIX="org.freedesktop.Anaconda.Addon"
ANACONDA_MODULE_SERVICE_PREFIX="org.freedesktop.Anaconda.Module"

DBUS_START_REPLY_SUCCESS=1

bus = SystemBus()
dbus = bus.get('org.freedesktop.DBus', 'org/freedesktop/DBus')

class Boss(object):
    """
        <node>
            <interface name='org.freedesktop.Anaconda.Boss'>
                <method name='EchoString'>
                    <arg type='s' name='question' direction='in'/>
                    <arg type='s' name='response' direction='out'/>
                </method>
                <method name='StartModulesSync'/>
                <method name='StartModules'/>
                <method name='Quit'/>
            </interface>
        </node>
    """

    def __init__(self, modules, addons=None):
        self._modules = modules
        self._addons = addons or []
        self._started_module_services = []
        self._failed_module_services = []

    @property
    def modules(self):
        return self._modules

    @property
    def addons(self):
        return self._addons

    @property
    def required_module_services(self):
        services = ["%s.%s" % (ANACONDA_MODULE_SERVICE_PREFIX, m)
                    for m in self.modules]
        services.extend(["%s.%s" % (ANACONDA_ADDON_SERVICE_PREFIX, a)
                         for a in self.addons])
        return services

    @property
    def running_module_services(self):
        # For our purpose, just this
        return self._started_module_services

    def EchoString(self, s):
        """returns whatever is passed to it"""
        logging.debug("%s: EchoString %s" % (self.__class__.__name__, s))
        return s

    def Quit(self):
        """removes the object from the DBUS connection and exits"""
        logging.debug("%s: Quit" % self.__class__.__name__)
        logging.debug("%s: sending Quit to all modules and addons" % self.__class__.__name__)
        for service in self.running_module_services:
            module = bus.get(service)
            # TODO: async
            module.Quit()
        GLib.timeout_add_seconds(1, loop.quit)

    def modules_starting_finished(self):
        # TODO: do we need some synchronization here?
        return set(self._started_module_services + self._failed_module_services) == set(self.required_module_services)

    def _start_service_cb(self, service, returned=None, error=None):
        """callback for dbus.StartServiceByName"""
        if error:
            logging.debug("%s: StartServiceByName %s error: %s" % (self.__class__.__name__, service, error))
            self._failed_module_services.append(service)
        elif returned:
            if returned == DBUS_START_REPLY_SUCCESS:
                logging.debug("%s: StartServiceByName %s started successfully (returned: %s)" % (self.__class__.__name__, service, returned))
                self._started_module_services.append(service)
            else:
                logging.debug("%s: StartServiceByName %s returned: %s" % (self.__class__.__name__, service, returned))
                self._failed_module_services.append(service)

        if self.modules_starting_finished():
            logging.debug("%s: modules starting finished, running: %s failed: %s" %
                          (self.__class__.__name__,
                           self._started_module_services,
                           self._failed_module_services))
            for service in self._started_module_services:
                module = bus.get(service)
                module.EchoString("Boss told me that all required modules were started: %s or failed: %s." %
                                  (self._started_module_services, self._failed_module_services))

            self.test_timezone_property()

    def test_timezone_property(self):
        logging.debug("%s: test_timezone_property" % self.__class__.__name__)
        tz_module = bus.get(ANACONDA_MODULE_SERVICE_PREFIX+".Timezone")
        tz = tz_module.TimezoneSpec
        logging.debug("%s: old timezone: %s" % (self.__class__.__name__, tz))
        #tz_module.setTimezoneSpec("tz_new")
        tz_module.TimezoneSpec = "tz_new"
        tz = tz_module.TimezoneSpec
        logging.debug("%s: new timezone: %s" % (self.__class__.__name__, tz))
        try:
            #tz_module.setTimezoneSpec("invalid_tz")
            tz_module.TimezoneSpec = "invalid_tz"
        except InvalidPropertyValueError as e:
            logging.debug("%s: new timezone error: %s" % (self.__class__.__name__, e))
        else:
            tz = tz_module.TimezoneSpec
            logging.debug("%s: new timezone: %s" % (self.__class__.__name__, tz))

    def StartModules(self):
        """starts anaconda modules (including addons)"""
        logging.debug("%s: StartModules started" % self.__class__.__name__)

        for service in self.required_module_services:
            logging.debug("%s: Starting %s" % (self.__class__.__name__, service))
            try:
                dbus.StartServiceByName(service, 0, callback=self._start_service_cb, callback_args=(service,))
            except Exception as e:
                self._failed_module_services.append(service)
                logging.debug("%s: exception %s:" % (self.__class__.__name__, e))

        logging.debug("%s: StartModules finished" % self.__class__.__name__)

    def StartModulesSync(self):
        """starts anaconda modules (including addons) synchronously"""
        logging.debug("%s: StartModulesSync started" % self.__class__.__name__)

        for service in self.required_module_services:
            logging.debug("%s: Starting %s" % (self.__class__.__name__, service))
            try:
                dbus.StartServiceByName(service, 0)
            except Exception as e:
                logging.debug("%s: exception %s:" % (self.__class__.__name__, e))
                self._failed_module_services.append(service)
            else:
                self._started_module_services.append(service)

        logging.debug("%s: StartModulesSync finished" % self.__class__.__name__)

    def find_addons(self):
        self._addons = []
        names = dbus.ListActivatableNames()
        for name in names:
            if name.startswith(ANACONDA_ADDON_SERVICE_PREFIX):
                self._addons.append(name[len(ANACONDA_ADDON_SERVICE_PREFIX)+1:])

    def initialize(self, addons=True):
        """initialize boss before publishing"""
        logging.debug("%s: intialize started" % self.__class__.__name__)
        if addons:
            self.find_addons()
        #time.sleep(random.randrange(1,4))

        # Check that no modules are running
        for service in self.required_module_services:
            if dbus.NameHasOwner(service):
                logging.error("%s: initialize: %s service has unexpected owner" %
                              (self.__class__.__name__, service))


        logging.debug("%s: intialize finished" % self.__class__.__name__)

logging.debug(80*"#")

# User does not have a binary
# Payload service does not have permissions (.conf file)
# Network service does not exist (doesn't have .service file)
#anaconda_modules = []
#anaconda_modules = ["Timezone", "Storage"]
#anaconda_modules = ["Timezone", "Storage", "Payload", "Network", "User"]
anaconda_modules = ["Timezone"]

boss = Boss(modules=anaconda_modules)
boss.initialize(addons=False)
bus.publish("org.freedesktop.Anaconda.Boss", boss)

def start():
    boss.EchoString("I am alive")
    return False

def start_modules_and_addons():
    boss.StartModules()
    #boss.StartModulesSync()
    return False

GLib.timeout_add_seconds(1, start_modules_and_addons)
loop.run()
