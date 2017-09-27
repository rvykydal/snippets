#!/usr/bin/python3

from gi.repository import GLib
from pydbus import SystemBus
import time
import random

loop = GLib.MainLoop()

import logging
logging.basicConfig(filename='/tmp/anaconda.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)s: %(funcName)s() %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S')
log = logging.getLogger("Monitor")


class Monitor(object):
    """
        <node>
            <interface name='org.freedesktop.Anaconda.Addon.Monitor'>
                <method name='EchoString'>
                    <arg type='s' name='question' direction='in'/>
                    <arg type='s' name='response' direction='out'/>
                </method>
                <method name='Quit'/>
            </interface>
        </node>
    """

    def EchoString(self, s):
        """returns whatever is passed to it"""
        log.debug(s)
        return s

    def Quit(self):
        """removes the object from the DBUS connection and exits"""
        log.debug("")
        GLib.timeout_add_seconds(1, loop.quit)

    def initialize(self):
        """initialize boss before publishing"""
        log.debug("started")
        time.sleep(random.randrange(4))
        log.debug("finished")

bus = SystemBus()
module = Monitor()
module.initialize()
bus.publish("org.freedesktop.Anaconda.Addon.Monitor", module)
loop.run()
