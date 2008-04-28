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

import os, threading, sys
import gtk
from mpdBrowserCovers import *
from idleObject import *

class mpdBrowserDatabase (threading.Thread, IdleObject):

    __gsignals__ =  { 
            # Collection scanned
            "scanned": (
           gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
            # status bar message
            "status": (
           gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING]),
            # Communication problem with mpd while looking at collection
            "exit": (
           gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
            }

    def __init__ (self, connection, path, stylizedCovers, hideMissing):
        """
            Read mpdBrowser conf, init connection and covers cache
        """
        
        threading.Thread.__init__ (self)
        IdleObject.__init__ (self)
        self.__stopevent = threading.Event ()

        self.__conn = connection
        self.__path = path
        self.__covers = mpdBrowserCovers (stylizedCovers, hideMissing)
        self.__covers.connect ("cache_message", self.__cacheMessageCb)
        self.__cacheMessage = ""
        
        
    def __cacheMessageCb (self, userData, info):
        """
            Update status bar message
        """
        self.__cacheMessage = info 
        
            
    def run (self):
        """
            run album scanning thread
        """
        try:
            albumList = []
            self.__conn.open ()
            self.__covers.createDirs ()
            # Get albums list
            albums = self.__conn.list ('album')

            nbAlbums = 0
            for album in albums:
                if self.__stopevent.isSet():
                    return
                # Get album genre, artist, cover and path
                tmpAlbums = self.__getAlbumInfos (album)
                albumList += tmpAlbums
                nbAlbums += len (tmpAlbums)

            self.__conn.close ()
            self.emit ("scanned", albumList)
        except:
            print "mpdBrowserDataBase::run(): "
            print sys.exc_info ()
            self.emit("status", _("Can't contact mpd!"))
        
        
    def stop (self):
        """
            Stop thread
        """
        self.__stopevent.set () 


    def getAlbums (self):
        """
            get albums => (genre, artist, path, pixbuf)
        """
        return self.__albums
        
        
    def __getAlbumInfos (self, album):
        """
            return album infos list (genre, artist, album, path, pixbuf)
        """
        list=[]
        currentPath=""

        self.__conn.open ()
        # Search infos for album
        infos = self.__conn.find ('album', album)

        for i in range (len (infos)):
            # Deal with missing tags
            if 'artist' not in infos[i].keys ():
                infos[i]['artist'] = _("Unknown")
            if 'album' not in infos[i].keys():
                infos[i]['album'] = _("Unknown")
            if 'genre' not in infos[i].keys():
                infos[i]['genre'] = _("Unknown")
                
            # Deal with multiple tags
            # Force an Attribute Error to be raise
            try:
                infos[i]['artist'].sort ()
                artist = infos[i]['artist'][0]
            except:
                artist = infos[i]['artist']
            try:
                infos[i]['genre'].sort ()
                genre = infos[i]['genre'][0]
            except:
                genre = infos[i]['genre']
                    
            path = os.path.dirname ( self.__path + infos[i]['file'])
            if currentPath != path: # We can have two albums with same name
                try:
                    pixbuf = self.__covers.get (path)
                    currentPath = path
                    list.append ((genre, artist, album, path, pixbuf))
                except: # Missing cover
                    pass

        self.__conn.close ()
        return list
