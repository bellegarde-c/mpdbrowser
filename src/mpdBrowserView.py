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
import os, sys
import gtk
from mpdBrowserDefine import *
from mpdBrowserCovers import *

class mpdBrowserView:

    def __init__ (self, showNames, stylizedCovers):
        """
            Create icon view
        """
        self.iconview = gtk.IconView ()

        self.__covers = mpdBrowserCovers (stylizedCovers)
        self.__covers.createDirs ()
        self.__emptyCover = gtk.gdk.pixbuf_new_from_file_at_size (empty, 128, 128)
        self.__case = gtk.gdk.pixbuf_new_from_file_at_size (case, 128, 128)
        self.__model = gtk.ListStore (gtk.gdk.Pixbuf, str)
        
        self.__albums = []
        
        if showNames:
            self.iconview.set_text_column (1)
       
        self.iconview.set_pixbuf_column (0)

        self.iconview.set_model (self.__model)    

        self.__items = []
        self.__realItemPos = [] # For filtered view
        self.__countItems = 0
        self.__showNames = showNames
        self.__coverUpdated = []


    def update (self):
        """
            Update covers in visible range
        """
        path = self.iconview.get_visible_range ()
        if path != None:
            for i in range (path[0][0], path[1][0] + 1):
                realPos = self.getRealItemPos ((i, ))
                if realPos not in self.__coverUpdated:
                    iter = self.__model.get_iter ((i,))
                    self.__coverUpdated.append (realPos)
                    try:
                        pixbuf = self.__covers.get (self.__albums[realPos]\
                                                                 [ALBUM_PATH])
                        self.__model.set_value (iter, 0, pixbuf)
                    except: # No update, cover missing
                        pass


        
    def updateColumns (self, showNames):
        """
            Update iconview columns
        """
        self.__showNames = showNames
        if not showNames and self.iconview.get_text_column () == 1:
            self.iconview.set_text_column (-1)
        elif self.iconview.get_text_column () == -1:
            self.iconview.set_text_column (1)

    
    def getRealItemPos (self, path):
        """
            Return real item position (used for filtered view)
            -1 for None path
        """
        if path == None:
            return -1
        else:
            return self.__realItemPos[path[0]]
            
            
    def clear (self):
        """
            Clear iconview
        """
        self.__countItems = 0
        self.__model.clear ()
        self.__realItemPos = []
        self.__coverUpdated = []
        self.__albums = []
        
        
    def visibleItemsNb (self):
        """
            Return visible items number
        """
        return self.__countItems
        
        
    def populate (self, albums, filter = "", filterType = 0):
        """
            Populate iconview
        """
        self.__albums  = albums
        i = 0
        self.__countItems = 0

        while i < len (self.__albums):
            try:
                if filter != "":
                    # Filter by Genre, Artist, Album
                    if (filter.lower() not in albums[i][ALBUM_GENRE].lower() or\
                        filterType not in (FILTER_ALL, FILTER_GENRE)) \
                    and (filter.lower() not in albums[i][ALBUM_ARTIST].lower() or\
                         filterType not in (FILTER_ALL, FILTER_ARTIST)) \
                    and (filter.lower() not in albums[i][ALBUM_NAME].lower() or\
                         filterType not in (FILTER_ALL, FILTER_ALBUM)): 
                        i+=1 
                        continue

                if len (albums[i][ALBUM_NAME]) > 25:
                    name = albums[i][ALBUM_NAME][:25] + "..."
                else:
                    name = albums[i][ALBUM_NAME]
      
                self.__model.append ([self.__emptyCover, name])
                self.__realItemPos.append (i)
                self.__countItems += 1
            except: 
                print "mpdBrowserView::populate():"
                print sys.exc_info ()
            i+=1
