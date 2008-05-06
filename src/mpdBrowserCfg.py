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

import ConfigParser
import os, sys

class mpdBrowserCfg:
    
    def __init__ (self):
        
        # Sections and options
        self.__options = {   
         "connection": ("mpdserver", "mpdport", "mpdpasswd", "collectionpath"),
         "window"    : ("x", "y","width","height"),
         "options"   : ("stylizedcovers", "shownames", 
                        "hidemissing", "covername", "coversize")
                         }
        # Defaults values
        self.__defaults = {
                            "mpdserver"     : "localhost",
                            "mpdport"       : 6600,
                            "mpdpasswd"     : "",
                            "collectionpath": "/var/lib/mpd/music",
                            "x"             : "",
                            "y"             : "",
                            "width"         : 640,
                            "height"        : 480,
                            "stylizedcovers": True,
                            "shownames"     : False,
                            "hidemissing"   : False,
                            "covername"     : "",
                            "coversize"     : 128
                           }
        # Defaults types
        self.__types = {
                            "mpdport"       : "int",
                            "x"             : "int",
                            "y"             : "int",
                            "width"         : "int",
                            "height"        : "int",
                            "stylizedcovers": "bool",
                            "shownames"     : "bool",
                            "hidemissing"   : "bool",
                            "covername"     : "string",
                            "coversize"     : "int"
                           }
                       
        self.__optionsValues = {}
        try:
            self.__cfgObj = ConfigParser.ConfigParser ()
            self.__cfgFile = os.path.expanduser ("~") + \
                             "/.config/mpdBrowser.conf"
            self.__cfgObj.read (self.__cfgFile)
            self.__read ()
        except:
            print sys.exc_info ()
    
    
    def __convert (self, option, value):
        """
            Convert an option from text to its type
        """
        try:
            if self.__types[option] == "int":
                return int (value)
            elif self.__types[option] == "bool":  
                if value == "True":
                    return True
                else:
                    return False
            else:
                return value
        except:
            return value
            
            
    def __readV (self, section, option):
        """
            return option value, otherwise default value
        """
        try:   
            value = self.__convert (option, self.__cfgObj.get (section, option))
        except:
            value = self.__defaults[option]
        return value  
         
              
    def __read (self):
        """
            Read options   
        """
        for section in self.__options.keys ():
            for option in self.__options[section]:
                if option != "null":
                    self.__optionsValues[option] = self.__readV (section, 
                                                                 option)
     
    def get (self, option):
        """
            return option value
        """
        return self.__optionsValues[option]
     
     
    def getAllOptions (self):
        """
            return options dict
        """
        return self.__optionsValues
        
    
    def __getSection (self, option):
        """
            return option section
        """
        for section in self.__options.keys ():
            for opt in self.__options[section]:
                if opt == option:
                    return section
        return None
        
        
    def set (self, option, value):
        """
            set option value at section
        """
        section = self.__getSection (option)
        try:
            self.__cfgObj.add_section (section)
        except: pass
        self.__optionsValues[option] = value
        self.__cfgObj.set (section, option, value)
        
    
    def write (self):
        """
            Write configuration file
        """
        self.__cfgObj.write (open (self.__cfgFile,'w'))
