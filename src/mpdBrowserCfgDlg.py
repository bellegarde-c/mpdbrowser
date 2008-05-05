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
        
        IdleObject.__init__ (self)
        
        self.__prefsWindow = gtk.Dialog (_("Preferences"), parent,
                                         flags=gtk.DIALOG_DESTROY_WITH_PARENT)
                                          
        self.__prefsWindow.set_role ('preferences')
        self.__prefsWindow.set_resizable (False)
        self.__prefsWindow.set_has_separator (False)
        
        hostLabel = gtk.Label (_("Host:"))
        hostEntry = gtk.Entry ()
        hostEntry.set_text (options["mpdserver"])
        
        portLabel = gtk.Label (_("Port:"))
        portEntry = gtk.Entry ()
        portEntry.set_text (str (options["mpdport"]))
        
        passwordLabel = gtk.Label (_("Password:"))
        passwordEntry = gtk.Entry ()
        passwordEntry.set_text (options["mpdpasswd"])
        passwordEntry.set_visibility (False)
        
        dirLabel = gtk.Label (_("Music dir:"))
        dirEntry = gtk.Entry ()
        dirEntry.set_text (options["collectionpath"])

        prefsConnFrame = gtk.Frame (_("Connection:"))
        table = gtk.Table (4, 2, False)
        table.set_col_spacings (3)
        table.attach (hostLabel, 1, 2, 1, 2)
        table.attach (hostEntry, 2, 3, 1, 2)
        table.attach (portLabel, 1, 2, 2, 3)
        table.attach (portEntry, 2, 3, 2, 3)
        table.attach (passwordLabel, 1, 2, 3, 4)        
        table.attach (passwordEntry, 2, 3, 3, 4)
        table.attach (dirLabel, 1, 2, 4, 5)        
        table.attach (dirEntry, 2, 3, 4, 5)
        prefsConnFrame.add (table)

        prefsOptFrame = gtk.Frame (_("Options:"))
        vboxOpt = gtk.VBox ()
        showNames = gtk.CheckButton (_("Show albums names"))
        showNames.set_active (options["shownames"])
        stylizedCovers = gtk.CheckButton (_("Stylized covers"))
        stylizedCovers.set_active (options["stylizedcovers"])
        hideMissing = gtk.CheckButton (_("Hide missing covers"))
        hideMissing.set_active (options["hidemissing"])
        
        hbox = gtk.HBox ()
        customCoverName = gtk.CheckButton (_("Custom cover name:"))
        if options["covername"] == "":
            active = False
        else:
            active = True
        customCoverName.set_active (active)
        coverName = gtk.Entry ()
        coverName.set_text (options["covername"])
        coverName.set_sensitive (active)
        customCoverName.connect ("clicked", self.__coverNameCb, coverName)
        hbox.pack_start (customCoverName, False, False, 0)
        hbox.pack_start (coverName, False, False, 0)
        
        vboxOpt.pack_start (showNames, False, False, 0)
        vboxOpt.pack_start (stylizedCovers, False, False, 0)
        vboxOpt.pack_start (hideMissing, False, False, 0)
        vboxOpt.pack_start (hbox, False, False, 0)
        prefsOptFrame.add (vboxOpt)
        
        prefsCacheFrame = gtk.Frame (_("Cache:"))
        clearButton = gtk.Button (_("Clear:"), gtk.STOCK_CLEAR)
        clearButton.connect ("clicked", self.__clearCache)
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
        buffer.insert_with_tags_by_name (iter, _("How play an album?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just click on it"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                         _("How enqueue an album?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just click on it with <Ctrl> pressed"))
        buffer.insert (iter, "\n\n")

        buffer.insert_with_tags_by_name (iter, _("How play a song?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, _("Just right click on album, then select song"))
        buffer.insert (iter, "\n\n")
        buffer.insert_with_tags_by_name (iter, 
                                         _("How enqueue a song?"), "bold")
        buffer.insert (iter, "\n")
        buffer.insert (iter, 
           _("Just right click on album with <Ctrl> pressed, then select song"))
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
                             
        self.__prefsWindow.connect ("destroy", self.__updateOpts, hostEntry, 
                                    portEntry, passwordEntry, dirEntry, 
                                    showNames, stylizedCovers, hideMissing,
                                    coverName)
        self.__prefsWindow.vbox.pack_start (notebook, False, False, 0)
        self.__prefsWindow.show_all ()
        closeButton.grab_focus ()
        
        
    def __close (self, data):
        """
            close and destroy pref widget
        """
        self.__prefsWindow.destroy ()
        
        
    def __updateOpts (self, data, hostEntry, portEntry, passwordEntry, dirEntry, 
                      showNames, stylizedCovers, hideMissing, coverName):
        """
            emit update_opt signal to update Options and reload view
        """
        self.__options = {
                            "mpdserver"     : hostEntry.get_text (),
                            "mpdport"       : int (portEntry.get_text ()),
                            "mpdpasswd"     : passwordEntry.get_text (),
                            "collectionpath": dirEntry.get_text (),
                            "shownames"     : showNames.get_active (),
                            "stylizedcovers": stylizedCovers.get_active (),
                            "hidemissing"   : hideMissing.get_active(),
                            "covername"     : coverName.get_text()
                          }
        # We need to clear cache
        if (coverName.get_text () != "" and 
                       self.__coverNameOrig != coverName.get_text ()) or  \
           (hideMissing.get_active () == True and \
                       self.__hideMissingOrig != hideMissing.get_active ()):
            self.__clearCache (None)
        self.emit ("update_opts")
     
     
    def __clearCache (self, data):
        """
            Clear covers cache
        """
        userDir = os.path.expanduser ("~")
        dirList = getDirListing ("%s/.local/share/mpdBrowser" % userDir, True)
        try:
            for item in dirList:    
                if os.path.isdir (item):
                    os.rmdir (item)
                else:
                    os.unlink (item)
            os.rmdir ("%s/.local/share/mpdBrowser" % userDir)
        except: 
            print "mpdBrowserCfgDlg::__clearCache(): "
            print sys.exc_info ()
      
      
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
