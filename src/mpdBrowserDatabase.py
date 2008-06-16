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

import os, threading, sys, time
import gtk
from mpdBrowserCovers import *
from idleObject import *

class mpdBrowserDatabase (threading.Thread, IdleObject):

    __gsignals__ =  { 
            # Collection scanned
            "scanned": (
           gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
            # Status bar message
            "status": (
           gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING]),
            # Progress bar percent
            "progress": (
           gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_FLOAT])
            }


    def __init__ (self, connection, path, update, stylizedCovers,
                  hideMissing, coverName, coverSize):
        """
            Read mpdBrowser conf, init connection and covers cache
        """
        
        threading.Thread.__init__ (self)
        IdleObject.__init__ (self)
        self.__stopevent = threading.Event ()

        self.__conn = connection
        self.__path = path
        self.__covers = mpdBrowserCovers (stylizedCovers, hideMissing, 
                                          coverName, coverSize)
        self.__update = update
        
            
    def run (self):
        """
            run album scanning thread
        """
        try:
            albumList = []
            currentPath=""
            
            if self.__update: # Wait for update to finish
                self.emit ("status", _("Updating MPD collection..."))
                try:
                    while True:
                        self.__conn.open ()
                        self.__conn.status () ['updating_db']
                        self.__conn.close ()
                        time.sleep (1)
                except: 
                    self.__conn.close () # Update finished

            # Get albums list
            self.emit ("status", _("Connecting to MPD..."))
            self.__conn.open ()
            mpdCollection = self.__conn.search ('album', "")
            self.__conn.close ()

            # Create internal DB
            totalItems = float (len (mpdCollection))
            nbItems = 0.0
            self.emit ("status", _("Loading albums..."))

            for item in mpdCollection:
                if self.__stopevent.isSet():
                    return

                path = os.path.dirname (self.__path + item['file'])                  
                if currentPath != path: # New album
                    try:
                        # Deal with missing tags
                        if 'artist' not in item.keys ():
                            item['artist'] = _("Unknown")
                        if 'album' not in item.keys():
                            item['album'] = _("Unknown") # Is that possible?
                        if 'genre' not in item.keys():
                            item['genre'] = _("Unknown")
                
                        # Deal with multiple tags
                        # Force an Attribute Error to be raise
                        try:
                            item['artist'].sort ()
                            artist = item['artist'][0]
                        except:
                            artist = item['artist']
                        try:
                            item['album'].sort ()
                            album = item['album'][0]
                        except:
                            album = item['album']
                        try:
                            item['genre'].sort ()
                            genre = item['genre'][0]
                        except:
                            genre = item['genre']

                        pixbuf = self.__covers.get (path, album, artist)
                        currentPath = path
                        albumList.append ((genre, artist, album, path, pixbuf))
                        
                    except: # Missing cover
                        pass
                if nbItems > totalItems - 50: # Want progress bar to go to 100%
                   self.emit ("progress", 1.0)
                elif not nbItems % 100: # Speed gain
                   self.emit ("progress", nbItems / totalItems)
                nbItems += 1
            
            # List is already sorted by genre, artist, album
            # Uncomment if mpd behaviour change
            #albumList.sort ()
            self.emit ("scanned", albumList)
        except:
            print "mpdBrowserDataBase::run(): "
            print sys.exc_info ()
            self.emit("status", _("Can't contact mpd!"))
            self.emit ("scanned", None)
        
        
    def stop (self):
        """
            Stop thread
        """
        self.__stopevent.set () 


    def getSongs (self, path, album):
        """
            Return song list for artist/album
        """
        list = []
        
        self.__conn.open ()
        infos = self.__conn.find ('album', album)
        self.__conn.close ()
        
        for i in range (len (infos)):
            # Deal with missing tags
            if 'title' not in infos[i].keys():
                infos[i]['title'] = _("Unknown")
                
            # Deal with multiple tags
            # Force an Attribute Error to be raise
            try:
                infos[i]['title'].sort ()
                title = infos[i]['title'][0]
            except:
                title = infos[i]['title']

            if os.path.dirname (self.__path + infos[i]['file']) == path:
                list.append ((title, self.__path + infos[i]['file']))
        return list
                
                
    def getAlbums (self):
        """
            get albums => (genre, artist, path, pixbuf)
        """
        return self.__albums
