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
from mpdBrowserUtils import *

class mpdBrowserView:

    def __init__ (self, showNames):
        """
            Create icon view
        """
        self.iconview = gtk.IconView ()
        
        self.__model = gtk.ListStore (gtk.gdk.Pixbuf, str)
       
        self.iconview.set_pixbuf_column (0)
        if showNames:
           self.iconview.set_text_column (1)
           
        self.iconview.set_model (self.__model)    
        
        self.__items = []
        self.__realItemPos = [] # For filtered view
        self.__countItems = 0
        self.__showNames = showNames

        
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
        
        
    def visibleItemsNb (self):
        """
            Return visible items number
        """
        return self.__countItems
        
        
    def populate (self, albums, filter = "", filterType = 0):
        """
            Populate iconview
        """

        i = 0
        self.__countItems = 0

        while i < len (albums):
            try:
                if filter != "":
                    # Filter by Genre, Artist, Album
                    if (filter.lower() not in albums[i][ALBUM_GENRE].lower() or \
                        filterType not in (FILTER_ALL, FILTER_GENRE)) \
                    and (filter.lower() not in albums[i][ALBUM_ARTIST].lower() or \
                         filterType not in (FILTER_ALL, FILTER_ARTIST)) \
                    and (filter.lower() not in albums[i][ALBUM_NAME].lower() or \
                         filterType not in (FILTER_ALL, FILTER_ALBUM)): 
                        i+=1 
                        continue
                
                name = cutStringAtSize (albums[i][ALBUM_NAME], 10, 40)
      
                self.__model.append ([albums[i][ALBUM_PIXBUF], name])
                self.__realItemPos.append (i)
                self.__countItems += 1
            except: 
                print "mpdBrowserView::populate():"
                print sys.exc_info ()
            i+=1
