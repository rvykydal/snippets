#!/usr/bin/python3

from gi.repository import GLib
from pydbus import SystemBus
import time
import random

loop = GLib.MainLoop()

import logging
logging.basicConfig(filename='/tmp/anaconda.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


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
        logging.debug("%s: EchoString %s" % (self.__class__.__name__, s))
        return s

    def Quit(self):
        """removes the object from the DBUS connection and exits"""
        logging.debug("%s: Quit" % self.__class__.__name__)
        GLib.timeout_add_seconds(1, loop.quit)

    def initialize(self):
        """initialize boss before publishing"""
        logging.debug("%s: intialize started" % self.__class__.__name__)
        time.sleep(random.randrange(4))
        logging.debug("%s: intialize finished" % self.__class__.__name__)

bus = SystemBus()
module = Monitor()
module.initialize()
bus.publish("org.freedesktop.Anaconda.Addon.Monitor", module)
loop.run()
