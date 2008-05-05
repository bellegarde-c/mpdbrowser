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

import gtk, gobject
import sys, os
from idleObject import *

empty = sys.prefix + "/share/pixmaps/mpdBrowser_empty.png"
if not os.path.exists (empty): empty = "../images/mpdBrowser_empty.png"
case = sys.prefix + "/share/pixmaps/mpdBrowser_case.png"
if not os.path.exists (case): case = "../images/mpdBrowser_case.png"


class MissingCover(Exception):
    pass


class mpdBrowserCovers (IdleObject):
                   
    def __init__ (self, stylizedCovers, hideMissing, coverName):
        """
            Load composite effect file if needed
        """
        IdleObject.__init__(self)
        
        if stylizedCovers == True:
            self.__case = gtk.gdk.pixbuf_new_from_file (case)
            self.__coverComp = True
        else:
            self.__coverComp = False
    
        self.__hideMissing = hideMissing
        self.__coverName = coverName
        
        
    def __findCover (self, dirPath):
        """
            Search a cover in dirPath
        """
        try:
            for name in os.listdir (dirPath):
                if name.endswith (".jpg") or name.endswith (".jpeg") or \
                   name.endswith (".png") or name.endswith (".gif"):
                    if (self.__coverName != ""):
                        if name.startswith (self.__coverName):
                            return dirPath + '/' + name
                        else:
                            return empty
                    else:
                        return dirPath + '/' + name

            return empty
        except:
            print sys.exc_info ()
            return empty


    def __coverComposite (self, cover, w, h):    # Thanks to Sonata devs ;)
        if float(w)/h > 0.5:
            # Rather than merely compositing the case on top of the artwork, 
            # we will scale the artwork so that it isn't covered by the case:
            spineRatio = float (60)/600 # From original png
            spineWidth = int (w * spineRatio)

            case = self.__case.scale_simple (w, h, gtk.gdk.INTERP_BILINEAR)
            # Scale pix and shift to the right on a transparent pixbuf:
            cover = cover.scale_simple (w-spineWidth, h, 
                                        gtk.gdk.INTERP_BILINEAR)
            blank = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, True, 8, w, h)
            blank.fill (0x00000000)
            cover.copy_area (0, 0, cover.get_width (), 
                             cover.get_height (), blank, spineWidth, 0)
            # Composite case and scaled pix:
            case.composite (blank, 0, 0, w, h, 0, 0,
                            1, 1, gtk.gdk.INTERP_BILINEAR, 250)
            del case
            return blank
        return cover


    def get (self, path):
        """
            Return pixbuf cover for album at path
        """
        # cache file will be _complete_path_to_album.jpg
        path_ = path.replace ("/", "_")
            
        if self.__coverComp:
            filePath = self.__shareDir + "/composite/" + path_ + ".jpg"
            if not os.access (filePath, os.F_OK):
                cover = self.__findCover (path)
                if cover == empty and self.__hideMissing:
                    raise MissingCover
                    
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (cover,
                                                               128, 128)
                if cover != empty:
                    w = pixbuf.get_width ()
                    h = pixbuf.get_height ()
                    pixbuf = self.__coverComposite (pixbuf, w, h)
                try:
                    pixbuf.save(filePath, "jpeg", {"quality":"100"})
                except: 
                    print "mpdBrowserCovers::get()/composite: "
                    print sys.exc_info ()

            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file (filePath)
        else:
            filePath = self.__shareDir + "/normal/" + path_ + ".jpg"
            if not os.access (filePath, os.F_OK):
                cover = self.__findCover (path)
                if cover == empty and self.__hideMissing:
                    raise MissingCover
                    
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (cover,
                                                               128, 128)
                try:
                    pixbuf.save(filePath, "jpeg", {"quality":"100"})
                except: 
                    print "mpdBrowserCovers::get()/normal: "
                    print sys.exc_info ()
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file (filePath)

        return pixbuf
    
        
    def createDirs (self):
        """
            Create cache directories
        """
        try:
            shareDir = os.path.expanduser ("~")
            for dir in ("/.local", "/share", "/mpdBrowser"):
                shareDir += dir
                if not os.access (shareDir, os.F_OK):
                    os.mkdir (shareDir)
                    
            if self.__coverComp and not \
               os.access (shareDir + "/composite", os.F_OK):
                os.mkdir (shareDir + "/composite")
                
            if not self.__coverComp and not \
               os.access (shareDir + "/normal", os.F_OK):
                os.mkdir (shareDir + "/normal")  
                
        except OSError: pass

        self.__shareDir = shareDir

            
