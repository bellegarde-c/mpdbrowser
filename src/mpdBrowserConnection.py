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

import mpd

class mpdBrowserConnection (mpd.MPDClient):

    def __init__ (self, server, port, passwd):
        """
            Set connection parameters
        """
        self.__server = server
        self.__port = port
        self.__passwd = passwd
        mpd.MPDClient.__init__(self)
        

    def updateOpts (self, server, port, passwd):
        """
            Set connection parameters
        """
        self.__server = server
        self.__port = port
        self.__passwd = passwd


    def open (self):
        """
            Open connection, will raise an exception if fails
        """
        self.connect (self.__server, self.__port)
        if self.__passwd != "":
            self.password (self.__passwd)

    
    def replace (self, item):
        """
            Replace current playlist with album
            Play it
            Will raise an exception if fails
        """
        self.clear ()
        self.add (item)
        self.play ()
        self.close ()
