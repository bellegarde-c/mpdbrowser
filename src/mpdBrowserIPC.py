# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA

import threading
from idleObject import *
import socket, select
import os, os.path

class mpdBrowserIPC_S(threading.Thread, IdleObject):

    __gsignals__ =  { 
            "present": (
                gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
            }
            
    def __init__ (self):
        """
            Thread initialisation
        """
        threading.Thread.__init__ (self)
        IdleObject.__init__ (self)
        self.__stopevent = threading.Event()

    def run (self):
        """
            Create mpd socket, bind it and listen to events
        """
        if os.path.exists ("/tmp/mpdBrowser-%s" % os.getuid ()): 
            os.remove ("/tmp/mpdBrowser-%s" % os.getuid ())
        self.__server = socket.socket (socket.AF_UNIX, socket.SOCK_RAW)
        self.__server.bind ("/tmp/mpdBrowser-%s" % os.getuid ())
        while not self.__stopevent.isSet () \
              and select.select ([self.__server], [], []):
            try:
                data = self.__server.recv (1024)
                if data == "start":
                    self.emit ("present")
                else:
                    break
            except: print sys.exc_info ()

    def stop (self):
        self.__stopevent.set ()         
    
class mpdBrowserIPC_C:        
    def __init__ (self, message):
        """
            Create client socket and send message
            Exception if no server running
        """
        client = socket.socket (socket.AF_UNIX, socket.SOCK_RAW)
        client.connect("/tmp/mpdBrowser-%s" % os.getuid ())  
        client.send (message)
