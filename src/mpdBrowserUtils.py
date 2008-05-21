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
  
import os


def cutStringAtSize (string, size, totalSize):
    """
        Format string for an iconview
        Replace ' ' by '\n' every size char
        Terminate string with ... if len > totalSize
    """
    if len (string) > totalSize:
        string = string[:totalSize] + "..."
        
    newString = ""
    lastSpace = -1
    i = 0
    sub = 0
    while i < len (string):
        if sub > size and string[i] == " ":
            newString += '\n'
            sub = 0
        else:
            newString += string[i]
        sub += 1
        i += 1
    return newString     
            
            
def getDirListing (dirPath, revert):
    """
        Return a list with dir content
        if revert == True, Files first, then dirs, then subdirs
        else, Dirs first, then subdirs, then files
    """
    dirList = []
    fileList = []
    for root, dirs, files in os.walk (dirPath, False):
        for name in files:
            fileList.append (os.path.join (root, name))
        for name in dirs:
            dirList.append (os.path.join (root, name))

    if revert == True:
        return fileList + dirList
    else:
        dirList.reverse ()
    return dirList + fileList
