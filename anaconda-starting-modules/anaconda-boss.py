#!/usr/bin/python3

from gi.repository import GLib
from pydbus import SystemBus
import time
import random
import os

loop = GLib.MainLoop()

import logging
logging.basicConfig(filename='/tmp/anaconda.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)s: %(funcName)s() %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger("Boss")

ANACONDA_ADDON_SERVICE_PREFIX="org.freedesktop.Anaconda.Addon"
ANACONDA_MODULE_SERVICE_PREFIX="org.freedesktop.Anaconda.Module"

DBUS_START_REPLY_SUCCESS=1

bus = SystemBus()
dbus = bus.get('org.freedesktop.DBus', '/org/freedesktop/DBus')

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
        self._service_watcher = None

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
        log.debug(s)
        return s

    def Quit(self):
        """removes the object from the DBUS connection and exits"""
        log.debug("sending Quit to all modules and addons")
        for service in self.running_module_services:
            module = bus.get(service)
            # TODO: async
            try:
                module.Quit()
            except Exception as e:
                log.debug(e)
        GLib.timeout_add_seconds(1, loop.quit)

    def modules_starting_finished(self):
        # TODO: do we need some synchronization here?
        return set(self._started_module_services + self._failed_module_services) == set(self.required_module_services)

    def _start_service_cb(self, service, returned=None, error=None):
        """callback for dbus.StartServiceByName"""
        if error:
            log.debug("%s error: %s" % (service,error))
            self._failed_module_services.append(service)
        elif returned:
            if returned == DBUS_START_REPLY_SUCCESS:
                log.debug("%s started successfully, returned: %s)" % (service, returned))
                self._started_module_services.append(service)
            else:
                log.debug("%s failed to start, returned: %s" % (service, returned))
                self._failed_module_services.append(service)

        self.check_modules_started()

    def check_modules_started(self):
        if self.modules_starting_finished():
            log.debug("modules starting finished, running: %s failed: %s" %
                      (self._started_module_services,
                       self._failed_module_services))
            for service in self._started_module_services:
                module = bus.get(service)
                module.EchoString("Boss told me that all required modules were started: %s or failed: %s." %
                                  (self._started_module_services, self._failed_module_services))
            return True
        else:
            return False

    def StartModules(self):
        """starts anaconda modules (including addons)"""
        log.debug("started")

        # Check that no modules are running
        for service in self.required_module_services:
            if dbus.NameHasOwner(service):
                log.error("service %s has unexpected owner" % service)

        for service in self.required_module_services:
            log.debug("Starting %s" % service)
            try:
                dbus.StartServiceByName(service, 0, callback=self._start_service_cb, callback_args=(service,))
            except Exception as e:
                self._failed_module_services.append(service)
                log.debug("exception: %s" % e)

        log.debug("finished")

    def StartModulesSync(self):
        """starts anaconda modules (including addons) synchronously"""
        log.debug("started")

        for service in self.required_module_services:
            log.debug("Starting %s" % service)
            try:
                dbus.StartServiceByName(service, 0)
            except Exception as e:
                log.debug("exception: %s" % e)
                self._failed_module_services.append(service)
            else:
                self._started_module_services.append(service)

        log.debug("finished")

    def find_addons(self):
        self._addons = []
        names = dbus.ListActivatableNames()
        for name in names:
            if name.startswith(ANACONDA_ADDON_SERVICE_PREFIX):
                self._addons.append(name[len(ANACONDA_ADDON_SERVICE_PREFIX)+1:])

    def initialize(self):
        """initialize boss before publishing"""
        log.debug("started")
        self.find_addons()
        #time.sleep(random.randrange(1,4))
        log.debug("finished")

    def _watch_starting_modules_cb(self, service, old, new):
        if service in self.required_module_services:
            if old:
                log.error("%s service owner %s disappeared - can't cope with this unexpected situation" % (service, old))
            if new:
                log.debug("%s appeared on the bus" % service)
                self._started_module_services.append(service)
                if self.check_modules_started():
                    self._service_watcher.disconnect()
                    log.debug("disconnected")

    def watch_starting_modules(self):
        for service in self.required_module_services:
            if dbus.NameHasOwner(service):
                self._started_module_services.append(service)
        # FIXME This is racy (can miss module started here)
        if self.check_modules_started():
            log.debug("all modules started, not watching")
        else:
            self._service_watcher = dbus.NameOwnerChanged.connect(self._watch_starting_modules_cb)
            log.debug("watching")

log.debug(80*"#")

# Only working modules
anaconda_modules = ["Timezone", "Storage"]
# Try Also disfunctional modules
# - User does not have a binary
# - Payload service does not have permissions (.conf file)
# - Network service does not exist (doesn't have .service file)
#anaconda_modules = ["Timezone", "Storage", "Payload", "Network", "User"]
# TODO: Crash1 crashes before publication on dbus
# TODO: Crash2 crashes after publication on dbus

boss = Boss(modules=anaconda_modules)
boss.initialize()
bus.publish("org.freedesktop.Anaconda.Boss", boss)

def start():
    boss.EchoString("I am alive")
    return False

def start_modules_and_addons():
    boss.StartModules()
    #boss.StartModulesSync()
    return False

def watch_starting_modules_and_addons():
    boss.watch_starting_modules()

#GLib.timeout_add_seconds(1, start_modules_and_addons)
GLib.idle_add(watch_starting_modules_and_addons)
loop.run()
