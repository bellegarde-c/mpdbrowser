#!/usr/bin/env python

import os, glob, shutil
import getopt, sys
import fileinput
from distutils.core import setup, Extension

def capture(cmd):
    return os.popen(cmd).read().strip()

def removeall(path):
	if not os.path.isdir(path):
		return

	files=os.listdir(path)

	for x in files:
		fullpath=os.path.join(path, x)
		if os.path.isfile(fullpath):
			f=os.remove
			rmgeneric(fullpath, f)
		elif os.path.isdir(fullpath):
			removeall(fullpath)
			f=os.rmdir
			rmgeneric(fullpath, f)

def rmgeneric(path, __func__):
	try:
		__func__(path)
	except OSError, (errno, strerror):
		pass

prefix="/usr/local"
try:                                
    opts, args = getopt.getopt(sys.argv[2:], "", ["prefix="])
    for opt, arg in opts:
        print opt + arg
        if opt == "--prefix":
            prefix = arg

    for line in fileinput.FileInput("src/mpdBrowser",inplace=1):    
        line = line.replace("@SYS@", prefix)
        sys.stdout.write(line)

    for line in fileinput.FileInput("src/mpdBrowserBase.py",inplace=1):    
        line = line.replace("@SYS@", prefix)
        sys.stdout.write(line)

    for line in fileinput.FileInput("src/mpdBrowserCovers.py",inplace=1):    
        line = line.replace("@SYS@", prefix)
        sys.stdout.write(line)

    for line in fileinput.FileInput("mpdBrowser.desktop.in",inplace=1):    
        line = line.replace("@SYS@", prefix)
        sys.stdout.write(line)

except getopt.GetoptError:
    pass

os.system("intltool-merge -d -u   po mpdBrowser.desktop.in mpdBrowser.desktop")

# Create mo files:
if not os.path.exists("mo/"):
	os.mkdir("mo/")
for lang in ('de', 'pl', 'ru', 'fr', 'zh_CN', 'sv', 'es', 'fi', 'uk', 'it', 'cs', \
             'nl', 'pt_BR', 'da', 'be@latin', 'et', 'ca', 'ar', 'tr', 'el_GR', 'sk', \
             'zh_TW', 'ja', 'sl'):
	pofile = "po/" + lang + ".po"
	mofile = "mo/" + lang + "/sonata.mo"
	if not os.path.exists("mo/" + lang + "/"):
		os.mkdir("mo/" + lang + "/")
	print "generating", mofile
	os.system("msgfmt %s -o %s" % (pofile, mofile))

setup(name='mpdBrowser',
        version="0.9.16",
        description='GTK+ client for the Music Player Daemon (MPD).',
        author='Cedric Bellegarde',
        author_email='gnumdk@gmail.com',
        url='',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: X11 Applications',
            'Intended Audience :: End Users/Desktop',
            'License :: GNU General Public License (GPL)',
            'Operating System :: Linux',
            'Programming Language :: Python',
            'Topic :: Multimedia :: Sound :: Players',
            ],
        packages=["mpdBrowser"],
        package_dir={"mpdBrowser": "src/"},
        scripts = ['src/mpdBrowser'],
        data_files=[('share/mpdBrowser', ['README', 'CHANGELOG', 'TODO', 'TRANSLATORS']),
                    ('share/applications', ['mpdBrowser.desktop']),
                    ('share/pixmaps', glob.glob('pixmaps/*')),
                    ('share/locale/pl/LC_MESSAGES', ['mo/pl/sonata.mo']),
                    ('share/locale/fr/LC_MESSAGES', ['mo/fr/sonata.mo']),
                    ('share/locale/it/LC_MESSAGES', ['mo/it/sonata.mo'])]
        )

# Cleanup (remove /build, /mo, and *.pyc files:
print "Cleaning up..."
try:
	removeall("build/")
	os.rmdir("build/")
except:
	pass
try:
	removeall("mo/")
	os.rmdir("mo/")
except:
	pass
try:
	for f in os.listdir("."):
		if os.path.isfile(f):
			if os.path.splitext(os.path.basename(f))[1] == ".pyc":
				os.remove(f)
except:
	pass
