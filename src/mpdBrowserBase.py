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


import gtk, pygtk, gobject
pygtk.require('2.0')
import os, sys
import subprocess
import gettext
from mpdBrowserDatabase import *
from mpdBrowserView import *
from mpdBrowserCfg import *
from mpdBrowserCfgDlg import *
from mpdBrowserIPC import *
from mpdBrowserConnection import *
   
icon = "@SYS@/share/pixmaps/mpdBrowser.png"
if not os.path.exists(icon): icon = "../pixmaps/mpdBrowser.png"

class mpdBrowserBase:

    def __init__ (self):    
        """
            Create Main Window
        """
        try:
            gettext.install ('mpdBrowser', sys.prefix + "/share" + "/locale",
			                unicode=1)
            gettext.textdomain ('mpdBrowser')
        except:
            print "mpdBrowserBase::__init__()/gettext: " + sys.exc_info ()
            
        self.__conf = mpdBrowserCfg ()
        self.__albums  = []
        self.__currentStatusMessage = ""
        
        # Create main window        
        self.__window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.__window.set_role ("mpdBrowser")

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file (icon)
            self.__window.set_icon (pixbuf)
        except:
            pass

        self.__window.connect ("configure_event", self.__configEventCb)
        self.__window.connect ("destroy", self.quit)
        self.__window.connect ("key-release-event", self.__windowEventsFilter)
        
        # Create IPC service
        self.__ipc = mpdBrowserIPC_S ()
        self.__ipc.connect ("present", self.__raiseCb)
        self.__ipc.start ()

        # Try to load window configuration
        try:
            self.__width = self.__conf.get ("width")
            self.__height = self.__conf.get ("height")
            self.__window.resize (self.__width,
                                  self.__height
                                 )                   
            self.__x = self.__conf.get ("x")
            self.__y = self.__conf.get ("y")
            if self.__x != "" and self.__y != "":
                self.__window.move (self.__x, self.__y)
        except ValueError:
            print "mpdBrowserBase::__init__()/conf:"
            print sys.exc_info ()
            try:
                mpdBrowserIPC_C("quit")
            except: 
                print "mpdBrowserBase::__init__()/IPC:"
                print sys.exc_info ()
            self.__ipc.stop ()
            sys.exit ()
            
        # Create Vbox elements (menubar, scrolled window, statusbar, filterbox)
        self.__scrolled = gtk.ScrolledWindow ()
        self.__scrolled.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                
        statusBox = gtk.HBox ();
        self.__progressBar = gtk.ProgressBar ()
        self.__statusBar = gtk.Statusbar ()
        self.__statusBar.set_no_show_all (True)
        self.__contId = self.__statusBar.get_context_id ("info")

        prefImg = gtk.Image ()
        prefImg.set_from_stock (gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU)
        self.__prefsButton = gtk.Button ()
        self.__prefsButton.add (prefImg)
        self.__prefsButton.connect ("clicked", self.__prefsCb, self.__window)
        
        playerImg = gtk.Image ()
        playerImg.set_from_stock (gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.__playerButton = gtk.Button ()
        self.__playerButton.add (playerImg)
        self.__playerButton.set_tooltip_text (self.__conf.get("mpdclient"))
        self.__playerButton.connect ("clicked", self.__playerCb, self.__window)

        statusBox.pack_start (self.__prefsButton, False, False, 0)
        statusBox.pack_start (self.__playerButton, False, False, 0)
        statusBox.pack_start (self.__progressBar, True, True, 0)
        statusBox.pack_start (self.__statusBar, True, True, 0)

        self.__filterBox = gtk.HBox ()
        self.__filterPattern = gtk.Entry ()
        self.__filterPattern.connect ("changed", self.__filterInsCb)
        self.__filterBox.pack_start (gtk.Label (_("Filter") + ":"),
                                     False, False, 5)
        self.__filterBox.pack_start (self.__filterPattern, True, True, 5)
        
        filterClearButton = gtk.Button ()
        filterClearButton.set_image (gtk.image_new_from_stock (gtk.STOCK_CLEAR,   
		                                                    gtk.ICON_SIZE_MENU))
        filterClearButton.connect ("clicked", self.__filterClearCb)
        self.__filterBox.pack_start (filterClearButton, False, False, 0)
        
        self.__filterCombo = gtk.combo_box_new_text ()
        self.__filterCombo.append_text (_("All"))
        self.__filterCombo.append_text (_("Artist"))
        self.__filterCombo.append_text (_("Album"))
        self.__filterCombo.append_text (_("Genre"))
        self.__filterCombo.set_active (0)
        self.__filterCombo.connect ("changed", self.__filterInsCb)
        self.__filterBox.pack_start (self.__filterCombo, False, False, 0)
        
        self.__filterCloseButton = gtk.Button ()
        self.__filterCloseButton.set_image (
                                      gtk.image_new_from_stock (gtk.STOCK_CLOSE,   
		                              gtk.ICON_SIZE_MENU)
                                           )
        self.__filterCloseButton.connect ("clicked", self.__filterHideCb)
        self.__filterBox.pack_start (self.__filterCloseButton, False, False, 0)
        
        self.__alwaysFiltering = self.__conf.get ("alwaysFiltering")
        self.__filterCloseButton.set_no_show_all (self.__alwaysFiltering)
        self.__filterBox.set_no_show_all (not self.__alwaysFiltering)
        
        # Try to load others options
        # Create Connection, DB and Iconview
        try:
            self.__path = self.__conf.get ("collectionpath") + "/"
            self.__conn = mpdBrowserConnection (self.__conf.get ("mpdserver"),
                                                self.__conf.get ("mpdport"),
                                                self.__conf.get ("mpdpasswd"))
            if self.__conf.get ("upstart"):
                try:
                    self.__conn.open ()
                    self.__conn.update ("/")
                    self.__conn.close ()
                    self.__initDB (True)
                except:
                    self.__initDB (False)
            else:
                self.__initDB (False)

            self.__view = mpdBrowserView (self.__conf.get ("shownames"))
            self.__view.iconview.connect ("event-after", 
                                          self.__iconviewEventsFilter)
        
    
	except:
            print "mpdBrowserBase::__init__()/IPC:"
            print sys.exc_info()
            try:
                mpdBrowserIPC_C ("quit")
            except: 
                print "mpdBrowserBase::__init__()/IPC:"
                print sys.exc_info ()
            self.__ipc.stop ()
            sys.exit ()
            
        self.__scanning ()     
        self.__DB.start ()
        self.__scrolled.add (self.__view.iconview)
        
        vbox = gtk.VBox ()
        vbox.pack_start (self.__filterBox, False, True, 0)   
        vbox.pack_start (self.__scrolled, True, True, 0)
        vbox.pack_start (statusBox, False, True, 0)
        self.__window.add (vbox)
              
        self.__window.show_all ()        
    
    
    def __scanning (self):
        """
            Set widgets for scanning
        """
        self.__prefsButton.set_sensitive (False)
        self.__window.set_title (_("Loading..."))          
                               
                                        
    def __initDB (self, update):
        """
            Init DB object
        """
        self.__DB = mpdBrowserDatabase (self.__conn,
                                        self.__path,
                                        update,
                                        self.__conf.get ("stylizedcovers"),
                                        self.__conf.get ("hidemissing"),
                                        self.__conf.get ("covername"),
                                        self.__conf.get ("coversize"))
        self.__DB.connect ("scanned", self.__scannedCb)
        self.__DB.connect ("status", self.__messageCb)
        self.__DB.connect ("progress", self.__progressCb)
        self.__statusBar.hide ()
        self.__progressBar.show ()

    
    def __windowEventsFilter (self, data, event):
        """
            events filter:
                - F5            -> update view
                - Ctrl F5       -> update collection
                - Ctrl f        -> show filter bar
		        - F3            -> Change add/enqueue bahaviour
        """
        if (event.get_state() & gtk.gdk.CONTROL_MASK) != 0:
            if event.keyval == gtk.keysyms.f and not self.__alwaysFiltering:
                if self.__filterBox.get_no_show_all ():
                    self.__motionEvent (-1)
                    self.__filterBox.set_no_show_all (False)
                    self.__filterBox.show_all ()
                    self.__filterPattern.grab_focus ()
                else:
                    self.__filterHideCb (None)
            elif event.keyval == gtk.keysyms.F5:
                    self.__view.clear ()
                    self.__DB.stop ()
                    self.__conn.open () 
                    self.__conn.update ("/")
                    self.__conn.close ()
                    self.__initDB (True)
                    self.__albums = []
                    self.__scanning ()
                    self.__DB.start ()
            elif event.keyval == gtk.keysyms.q:
                    self.quit (None)
        elif event.keyval == gtk.keysyms.F5:
            self.__view.clear ()
            self.__DB.stop ()
            self.__initDB (False)
            self.__albums = []
            self.__scanning ()
            self.__DB.start ()
        elif event.keyval == gtk.keysyms.F3:
            self.__conf.set ("queuebydefault", 
		                                 not self.__conf.get ("queuebydefault"))
            if self.__conf.get ("queuebydefault"):
    		    self.__messageCb (None, _("Queue by default"))
            else:
                self.__messageCb (None, _("Replace by default"))
		                
        
    def __iconviewEventsFilter (self, iconview, event):
        """
            events filter:
                - Left click    -> play/enqueue album
                - Right click   -> popup song list
                - Middle click  -> clear playlist
                - F5            -> update view
                - Ctrl F5       -> update collection
                - Ctrl f        -> show filter bar
		        - F3            -> Change add/enqueue bahaviour
        """
        try:
            if event.type == gtk.gdk.BUTTON_RELEASE:
                x,y = event.get_coords ()
                path = iconview.get_path_at_pos (int (x), int (y))
                pos = self.__view.getRealItemPos (path)
                iconview.unselect_all ()
                if pos != -1:
                    if (event.get_state() & gtk.gdk.CONTROL_MASK) != 0:
                        if self.__conf.get ("queuebydefault"):
                            action = MPD_REPLACE
                        else:
                            action = MPD_ENQUEUE
                    else:
                         if self.__conf.get ("queuebydefault"):
                            action = MPD_ENQUEUE
                         else:
                            action = MPD_REPLACE
                    if event.button == 3:
                        self.__popupSongs (pos, action)
                    elif event.button == 2:
                        self.__conn.open ()
                        self.__conn.clear ()
                        self.__conn.close ()
                    elif event.button == 1:
                        self.__playAlbum (pos, event.button, action)
            elif event.type == gtk.gdk.MOTION_NOTIFY:
                x,y = event.get_coords ()
                path = iconview.get_path_at_pos (int (x), int (y))
                pos = self.__view.getRealItemPos (path)  
                self.__motionEvent (pos)
            elif event.type == gtk.gdk.KEY_RELEASE:
                if event.keyval == gtk.keysyms.Return:
                    try:
                        (path, cell) = iconview.get_cursor ()
                        pos = self.__view.getRealItemPos (path)
                        iconview.unselect_all ()
                        if pos != -1:
                            self.__playAlbum (pos, 1)
                    except: pass # no cursor
                
        except:
            print "mpdBrowserBase::__eventsFilter():"
            print sys.exc_info ()
         
            
    def __prefsCb (self, userData, parent):
        """
            Show prefs dialog
        """
        self.__prefsDialog = mpdBrowserCfgDlg (parent, 
                                               self.__conf.getAllOptions ())
        self.__prefsDialog.connect ("update_opts", self.__updateOpts)
    

    def __playerCb (self, userData, parent):
        """
            Run prefered mpd client
        """
        subprocess.Popen([self.__conf.get("mpdclient")])

       
    def __filterClearCb (self, userData):
        """
            Clear filter entry
        """
        self.__filterPattern.set_text ("")


    def __filterInsCb (self, userData):
        """
            Filter view
        """
        self.__view.clear ()
        self.__view.populate (self.__albums,
                              self.__filterPattern.get_text (),
                              self.__filterCombo.get_active ())
        self.__motionEvent (-1)
        

    def __filterHideCb (self, userData):
        """
            hide filter widget
        """
        self.__filterBox.set_no_show_all (True)
        self.__filterBox.hide ()
        self.__filterPattern.set_text ("")
        self.__view.iconview.grab_focus ()
        
        
    def __updateOpts (self, data):
        """
            Save options, update DB and/or View
        """
        updateViewOpts = "shownames"
        updateDbOpts   =  ("mpdserver", "mpdport", "mpdpasswd", 
                           "collectionpath", "stylizedcovers", "hidemissing",
                           "covername", "coversize")
        updateUiOpts = "alwaysFiltering"
        updateView = False
        updateDb = False
        updateUi = False
        
        # search for change in options
        options = self.__prefsDialog.getUserOptions ()
        oldOptions = self.__conf.getAllOptions ()
        for option in options.keys ():
            if options[option] != oldOptions[option]:
                self.__conf.set (option, options[option])
                if option in updateViewOpts:
                    updateView = True
                elif option in updateDbOpts:
                    updateDb = True
                elif option in updateUiOpts:
                    updateUi = True
        self.__conf.write ()
        
        if updateDb:
            self.__scanning ()
            self.__path = self.__conf.get("collectionpath") + "/"

            self.__conn.updateOpts (self.__conf.get ("mpdserver"),
                                    self.__conf.get ("mpdport"),
                                    self.__conf.get ("mpdpasswd"))
            self.__view.clear ()
            self.__DB.stop ()
            self.__initDB (False)
            self.__albums = []
            self.__DB.start ()
            
        if updateView:
            self.__view.updateColumns (self.__conf.get ("shownames"))
        
        if updateUi:
            self.__alwaysFiltering = self.__conf.get ("alwaysFiltering")
            self.__filterCloseButton.set_no_show_all (self.__alwaysFiltering)
            self.__filterBox.set_no_show_all (not self.__alwaysFiltering)
            if self.__alwaysFiltering:
                self.__filterCloseButton.hide ()
                self.__filterBox.show_all ()
            else:
                self.__filterCloseButton.show ()
                self.__filterBox.hide ()

        self.__view.iconview.grab_focus ()
        
        
    def __raiseCb (self, data):
        """
            Raise main window
        """
        self.__window.present ()

    
    def __messageCb (self, data, info):
        """
            Update status/progress bar message
        """
        try:
            if not len (self.__albums): # Progress bar visible
                self.__progressBar.set_text (info)
            else:
                self.__statusBar.show ()
                self.__progressBar.hide ()
                self.__statusBar.push (self.__contId, info);
        except: 
            print "mpdBrowserBase::__statusCb():"
            print sys.exc_info ()
           
              
    def __menuItemCb (self, item, path, action):
        """
            Play selected song
        """
        try:
            self.__conn.open ()
            if action == MPD_REPLACE:
                self.__conn.replace (path.replace (self.__path, ""))
            else:
                self.__conn.add (path.replace (self.__path, ""))
            self.__conn.close ()
        except:
            print "mpdBrowserBase::__menuItemCb():"
            print sys.exc_info ()
            self.__statusBar.push (self.__contId, _("Can't contact mpd!"))
            
               
    def __progressCb (self, data, percent):
        """
            update progress bar
        """
        self.__progressBar.set_fraction (percent)
        
        
    def __scannedCb (self, data, albums):
        """
            Add albums to iconview
        """
        if albums != None: # We have albums!
            self.__progressBar.set_text ("")
            self.__window.set_title ("mpdBrowser")
            self.__statusBar.push (self.__contId, 
                                   _("You have %i albums.") % len (albums))
            self.__albums = albums
            self.__view.populate (self.__albums,
                                  self.__filterPattern.get_text (),
                                  self.__filterCombo.get_active ())
            self.__progressBar.hide ()
            self.__statusBar.show ()
            self.__progressBar.set_fraction (0.0)
            self.__view.iconview.grab_focus ()

        self.__window.set_title ("mpdBrowser")
        self.__prefsButton.set_sensitive (True)
        
   
    def __configEventCb (self, widget, allocation):
        """
            Track main window size/pos changes
        """
        self.__width, self.__height = self.__window.get_size ()
        self.__x, self.__y = self.__window.get_position ()


    def __motionEvent (self, pos):
        """
            Motion event (update status bar)
        """
        nbItems = self.__view.visibleItemsNb ()
        if nbItems:
            if pos != -1:
                statusMessage = "%s  -  %s" % (self.__albums[pos][ALBUM_ARTIST],
                                               self.__albums[pos][ALBUM_NAME])
            else:
                statusMessage = "%s albums" % nbItems
    
            if statusMessage != self.__currentStatusMessage:
                self.__currentStatusMessage = statusMessage
                self.__statusBar.push (self.__contId, statusMessage);
        
    
    def __popupSongs (self, pos, action):
        """
            Popup menu with songs list
        """
        album = self.__albums[pos][ALBUM_NAME]
        path = self.__albums[pos][ALBUM_PATH]
        popupMenu = gtk.Menu()
        for song in self.__DB.getSongs (path, album):
            if len (song[0]) > STRING_SONG_SIZE:
                name = song[0][:STRING_SONG_SIZE] + "..."
            else:
                name = song[0]
            item =  gtk.MenuItem (name)
            item.connect ("activate", self.__menuItemCb, song[1], action)
            popupMenu.add (item)
        popupMenu.show_all()
        popupMenu.popup(None, None, None, 1, 0)
                
        
    def __playAlbum (self, pos, button, action):
        """
            Play selected album
        """
        try:
            self.__conn.open ()
            album = self.__albums[pos][ALBUM_PATH]
            if action == MPD_REPLACE:
                self.__conn.replace (album.replace (self.__path, ""))
            else:
                self.__conn.add (album.replace (self.__path, ""))
            self.__conn.close ()
        except:
            print "mpdBrowserBase::__playAlbum():"
            print sys.exc_info ()
            self.__statusBar.push (self.__contId, _("Can't contact mpd!"))
            
            
    def stopThreads(self):
        """
            Stop all running threads
        """
        self.__DB.stop ()
        mpdBrowserIPC_C ("quit")
        self.__ipc.stop ()
        
        
    def main (self):
        """
            Gtk Main Loop
        """
        gtk.main ()
       
       
    def quit (self, widget):
        """
            Stop running threads, save conf and quit
        """
        self.stopThreads ()
        self.__conf.set ("width", self.__width)
        self.__conf.set ("height", self.__height)
        self.__conf.set ("x", self.__x)        
        self.__conf.set ("y", self.__y)  
        self.__conf.write ()      
        gtk.main_quit ()
