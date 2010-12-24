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
import gtk, pango
import os, sys
from idleObject import *
from mpdBrowserUtils import *

class mpdBrowserCfgDlg (IdleObject):

    __gsignals__ =  { 
            "update_opts": (    # update options
                gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []) 
            }

    def __init__ (self, parent, options):
        """
            Create prefs window and set callbacks
        """
    
        self.__options = {}
        self.__coverNameOrig = options["covername"]
        self.__hideMissingOrig = options["hidemissing"]
        self.__coverSizeOrig = options["coversize"]
        self.__mpdClient = options["mpdclient"]
        
        IdleObject.__init__ (self)
        
        self.__prefsWindow = gtk.Dialog (_("Preferences"), parent,
                                         flags=gtk.DIALOG_DESTROY_WITH_PARENT)
                                          
        self.__prefsWindow.set_role ('preferences')
        self.__prefsWindow.set_resizable (False)
        self.__prefsWindow.set_has_separator (False)
        
        hostLabel = gtk.Label (_("Host:"))
        self.__hostEntry = gtk.Entry ()
        self.__hostEntry.set_text (options["mpdserver"])
        
        portLabel = gtk.Label (_("Port:"))
        self.__portEntry = gtk.Entry ()
        self.__portEntry.set_text (str (options["mpdport"]))
        
        passwordLabel = gtk.Label (_("Password:"))
        self.__passwordEntry = gtk.Entry ()
        self.__passwordEntry.set_text (options["mpdpasswd"])
        self.__passwordEntry.set_visibility (False)
        
        dirLabel = gtk.Label (_("Music dir:"))
        self.__dirEntry = gtk.Entry ()
        self.__dirEntry.set_text (options["collectionpath"])

        mpdClientLabel = gtk.Label (_("Mpd client:"))
        self.__mpdClient = gtk.Entry ()
        self.__mpdClient.set_text (options["mpdclient"])
        
        prefsConnFrame = gtk.Frame (_("Connection:"))
        table = gtk.Table (5, 2, False)
        table.set_col_spacings (3)
        table.attach (hostLabel, 0, 1, 0, 1)
        table.attach (self.__hostEntry, 1, 2, 0, 1)
        table.attach (portLabel, 0, 1, 1, 2)
        table.attach (self.__portEntry, 1, 2, 1, 2)
        table.attach (passwordLabel, 0, 1, 2, 3)        
        table.attach (self.__passwordEntry, 1, 2, 2, 3)
        table.attach (dirLabel, 0, 1, 3, 4)        
        table.attach (self.__dirEntry, 1, 2, 3, 4)
        table.attach (mpdClientLabel, 0, 1, 4, 5)
        table.attach (self.__mpdClient, 1, 2, 4, 5)
        prefsConnFrame.add (table)

        prefsOptFrame = gtk.Frame (_("Options:"))
        vboxOpt = gtk.VBox ()
        self.__upStart = gtk.CheckButton (_("Update collection at startup"))
        self.__upStart.set_active (options["upstart"])
        self.__showNames = gtk.CheckButton (_("Show albums names"))
        self.__showNames.set_active (options["shownames"])
        self.__stylizedCovers = gtk.CheckButton (_("Stylized covers"))
        self.__stylizedCovers.set_active (options["stylizedcovers"])
        self.__hideMissing = gtk.CheckButton (_("Hide missing covers"))
        self.__hideMissing.set_active (options["hidemissing"])
        self.__alwaysFiltering = gtk.CheckButton (_("Always show filter bar"))
        self.__alwaysFiltering.set_active (options["alwaysFiltering"])
        self.__queueByDefault = gtk.CheckButton (_("Queue by default"))
        self.__queueByDefault.set_active (options["queuebydefault"])
                
        customCoverName = gtk.CheckButton (_("Custom cover name:"))
        if options["covername"] == "":
            active = False
        else:
            active = True
        customCoverName.set_active (active)
        self.__coverName = gtk.Entry ()
        self.__coverName.set_text (options["covername"])
        self.__coverName.set_sensitive (active)
        customCoverName.connect ("clicked", self.__coverNameCb, 
                                            self.__coverName)
        
        coverSizeLabel = gtk.Label (_("Covers size:"))
        self.__coverSize = gtk.HScale ()
        self.__coverSize.set_range (64, 256)
        self.__coverSize.set_increments (1, 1)
        self.__coverSize.set_digits(0)
        self.__coverSize.set_value (options["coversize"])

        table = gtk.Table (2, 2, False)
        table.set_homogeneous (True)
        table.set_col_spacings (3)
        table.attach (customCoverName, 0, 1, 0, 1)
        table.attach (self.__coverName, 1, 2, 0, 1)
        table.attach (coverSizeLabel, 0, 1, 1, 2)
        table.attach (self.__coverSize, 1, 2, 1, 2)
        
        vboxOpt.pack_start (self.__upStart, False, False, 0)
        vboxOpt.pack_start (self.__showNames, False, False, 0)
        vboxOpt.pack_start (self.__stylizedCovers, False, False, 0)
        vboxOpt.pack_start (self.__hideMissing, False, False, 0)
        vboxOpt.pack_start (self.__alwaysFiltering, False, False, 0)
        vboxOpt.pack_start (self.__queueByDefault, False, False, 0)
        vboxOpt.pack_start (table, False, False, 0)
        prefsOptFrame.add (vboxOpt)
        
        prefsCacheFrame = gtk.Frame (_("Cache:"))
        clearButton = gtk.Button (_("Clear:"), gtk.STOCK_CLEAR)
        clearButton.connect ("clicked", clearCache)
        prefsCacheFrame.add (clearButton)

        vbox = gtk.VBox ()
        vbox.pack_start (prefsConnFrame, False, False, 0)
        vbox.pack_start (prefsOptFrame, False, False, 0)
        vbox.pack_start (prefsCacheFrame, False, False, 10)

        text = gtk.TextView ()
        buffer = gtk.TextBuffer ()
        buffer.create_tag ("bold", weight=pango.WEIGHT_BOLD)
        iter = buffer.get_iter_at_offset (0)
        buffer.insert_with_tags_by_name (iter,
                            "Copyleft Cedric Bellegarde (gnumdk@gmail.com)",
                            "bold")
        buffer.insert (iter, "\n\n")  
        buffer.insert_with_tags_by_name (iter, 
                                         _("How to play an album?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just click on it"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                         _("How to enqueue an album?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just click on it with Ctrl pressed"))
        buffer.insert (iter, "\n\n")

        buffer.insert_with_tags_by_name (iter, _("How to play a song?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just right click on album, then select song"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                         _("How to enqueue a song?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, 
           _("Just right click on album with Ctrl pressed, then select song"))
        buffer.insert (iter, "\n\n")
        
        buffer.insert_with_tags_by_name (iter, _("How to add a cover?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just copy an image to album folder"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                      _("How to search for something?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just press Ctrl + f"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                      _("How to refresh view?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just press F5"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                      _("How to refresh collection?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just press Ctrl + F5"))
        
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                              _("How to switch between enqueue modes?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just press F3"))
    
        text.set_editable (False)
        text.set_buffer (buffer)

        scrolled = gtk.ScrolledWindow ()
        scrolled.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add (text)

        notebook = gtk.Notebook ()        
        prefsLabel = gtk.Label (_("Preferences"))
        notebook.append_page (vbox, prefsLabel) 
        infosLabel = gtk.Label (_("Informations"))
        notebook.append_page (scrolled, infosLabel)
        
        closeButton = self.__prefsWindow.add_button (gtk.STOCK_CLOSE, 
                                                     gtk.RESPONSE_CLOSE)
        closeButton.connect ("clicked", self.__close)
                             
        self.__prefsWindow.connect ("destroy", self.__updateOpts)
        self.__prefsWindow.vbox.pack_start (notebook, False, False, 0)
        self.__prefsWindow.show_all ()
        closeButton.grab_focus ()
        
        
    def __close (self, data):
        """
            close and destroy pref widget
        """
        self.__prefsWindow.destroy ()
        
        
    def __updateOpts (self, data):
        """
            emit update_opt signal to update Options and reload view
        """
        self.__options = {
                        "mpdserver"      : self.__hostEntry.get_text (),
                        "mpdport"        : int (self.__portEntry.get_text ()),
                        "mpdpasswd"      : self.__passwordEntry.get_text (),
                        "collectionpath" : self.__dirEntry.get_text (),
                        "upstart"        : self.__upStart.get_active (),
                        "shownames"      : self.__showNames.get_active (),
                        "stylizedcovers" : self.__stylizedCovers.get_active (),
                        "hidemissing"    : self.__hideMissing.get_active (),
                        "alwaysFiltering": self.__alwaysFiltering.get_active (),
                        "covername"      : self.__coverName.get_text (),
                        "coversize"      : int (self.__coverSize.get_value ()),
                        "mpdclient"      : self.__mpdClient.get_text (),
                        "queuebydefault" : self.__queueByDefault.get_active ()
                          }
                          
        # We need to clear cache
        if self.__coverNameOrig != self.__coverName.get_text () \
           or \
           self.__coverSizeOrig != int (self.__coverSize.get_value ()) \
           or \
          (self.__hideMissing.get_active () == True and 
           self.__hideMissingOrig != self.__hideMissing.get_active ()):
           
            clearCache (None)
            
        self.emit ("update_opts")
     
     
    def __coverNameCb (self, button, entry):
        """
            Enable cover name entry
        """
        if button.get_active():
            entry.set_sensitive (True)
        else:
            entry.set_text ("")
            entry.set_sensitive (False)
        
        
    def getUserOptions (self):
        """
            Return new user options
        """
        return self.__options               
