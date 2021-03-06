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
import cairo, pangocairo, pango
import sys, os
from mpdBrowserUtils import *
from mpdBrowserDefine import *
from idleObject import *

case = "@SYS@/share/pixmaps/mpdBrowser_case.png"
if not os.path.exists (case): case = "../pixmaps/mpdBrowser_case.png"

class MissingCover(Exception):
    pass

class mpdBrowserCovers (IdleObject):
                   
    def __init__ (self, stylizedCovers, hideMissing, coverName, coverSize):
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
        self.__coverSize = coverSize
        self.__createDirs ()
        self.__initEmpty ()
        
    
    def __initEmpty (self):
        """
	    Initialise empty cover:
	    	- User cover first
		- System cover then
		- Fallback to install dir if no covers
        """   
        self.__emptyPath = os.path.expanduser ("~") + \
                       "/.local/share/mpdBrowser/empty.png"
        if not os.path.exists (self.__emptyPath):
            self.__emptyPath = sys.prefix + "/share/pixmaps/mpdBrowser_empty.png"
            if not os.path.exists (self.__emptyPath): 
                self.__emptyPath = "../pixmaps/mpdBrowser_empty.png"

        self.__empty = gtk.gdk.pixbuf_new_from_file_at_size (self.__emptyPath,
                                                             self.__coverSize, 
                                                             self.__coverSize)

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
                        return dirPath + '/' + name

            return self.__emptyPath
        except:
            print sys.exc_info ()
            return self.__emptyPath


    def __coverComposite (self, cover, pixbuf, w, h, spineRatio):
        """
            Compose cover with pixbuf
        """
        # Thanks to Sonata devs ;)
        if float(w)/h > 0.5:
            # Rather than merely compositing the case on top of the artwork, 
            # we will scale the artwork so that it isn't covered by the case:
            spineWidth = int (w * spineRatio)

	    # We wan't to preserve aspect ratio
            if h >= w - spineWidth:
                h -= spineWidth
                
            case = pixbuf.scale_simple (w, h, gtk.gdk.INTERP_BILINEAR)
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


    def __coverCreateFromText (self, text):
        """
            Create a cover from text
        """
	#TODO Now write png to CAIRO_COVER
	# Should be better to keep it in memory and let cache manager
	# copy it to mpdBrowser cache.
	# How convert a CAIRO Image Surface to a GTK PIXBUF?

        # Setup Cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 
                                     self.__coverSize, self.__coverSize)
        ctx = cairo.Context(surface)

        pcr = pangocairo.CairoContext (ctx)
        layout = pcr.create_layout ()
        layout.set_width (self.__coverSize * pango.SCALE)
        layout.set_wrap (pango.WRAP_WORD_CHAR)
        layout.set_alignment (pango.ALIGN_CENTER)
        
        if len (text) > COVER_LENGTH:
            text = text[:COVER_LENGTH-3] + "..."

        layout.set_markup (
                 '''<span foreground="black" font_desc="Sans %s">%s</span>'''\
                 % (self.__coverSize/12, text.replace ("&", "&amp;"))
                          )
        ctx.move_to (0, self.__coverSize/layout.get_line_count())
        ctx.save ()
        pcr.show_layout (layout)
        surface.write_to_png(CAIRO_COVER)


    def __createDirs (self):
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


    def get (self, path, album, artist):
        """
            Return pixbuf cover for album at path
            Write artist and album into a pixbuf if no cover
        """
        # cache file will be _complete_path_to_album.jpg
        path_ = path.replace ("/", "_")
            
        if self.__coverComp:
            filePath = self.__shareDir + "/composite/" + path_ + ".jpg"
            if not os.access (filePath, os.F_OK): # No cache
                coverPath = self.__findCover (path)
                
                if coverPath == self.__emptyPath and self.__hideMissing:
                    raise MissingCover
                    
                if coverPath != self.__emptyPath: # get composited cover
                    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (
                                                               coverPath,
                                                               self.__coverSize, 
                                                               self.__coverSize
                                                                  )
                    w = pixbuf.get_width ()
                    h = pixbuf.get_height() 
                    pixbuf = self.__coverComposite (pixbuf, self.__case, 
                                                    w, h, SPINE_RATIO)
                else: # add album name to empty composited cover
                    self.__coverCreateFromText ("<b>" + artist + \
                                                "</b>\n\n" + album)
                    cairoCover = gtk.gdk.pixbuf_new_from_file_at_size (
                                                               CAIRO_COVER,
                                                               self.__coverSize,
                                                               self.__coverSize
                                                                      )
                    os.unlink (CAIRO_COVER)
                    w = self.__empty.get_width ()
                    h = self.__empty.get_height ()
                    tmpPix = self.__coverComposite (self.__empty, cairoCover,
                                                    w, h, 0.0)
                    w = tmpPix.get_width ()
                    h = tmpPix.get_height ()                  
                    pixbuf = self.__coverComposite (tmpPix, self.__case,
                                                    w, h, SPINE_RATIO)
                    del tmpPix
                    del cairoCover
                try:
                    pixbuf.save(filePath, "jpeg", {"quality":"100"})
                except: 
                    print "mpdBrowserCovers::get()/composite: "
                    print sys.exc_info ()

            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file (filePath)
        else:
            filePath = self.__shareDir + "/normal/" + path_ + ".jpg"
            if not os.access (filePath, os.F_OK): # No cache
                coverPath = self.__findCover (path)
                if coverPath == self.__emptyPath and self.__hideMissing:
                    raise MissingCover
                
                if coverPath != self.__emptyPath: # get cover 
                    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (
                                                               coverPath,
                                                               self.__coverSize, 
                                                               self.__coverSize
                                                                  )
                else: # add album name to empty cover
                    self.__coverCreateFromText ("<b>" + artist + \
                                                "</b>\n\n" + album)
                    cairoCover = gtk.gdk.pixbuf_new_from_file_at_size (
                                                               CAIRO_COVER,
                                                               self.__coverSize,
                                                               self.__coverSize
                                                                      )
                    os.unlink (CAIRO_COVER)
                    w = self.__empty.get_width ()
                    h = self.__empty.get_height ()
                    pixbuf = self.__coverComposite (self.__empty, cairoCover,
                                                    w, h, 0.0)    
                    del cairoCover
                try:
                    pixbuf.save(filePath, "jpeg", {"quality":"100"})
                except: 
                    print "mpdBrowserCovers::get()/normal: "
                    print sys.exc_info ()
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file (filePath)

        return pixbuf
            
