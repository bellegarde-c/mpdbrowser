#!/usr/bin/env python

# $HeadURL: http://svn.berlios.de/svnroot/repos/sonata/trunk/setup.py $
# $Id: setup.py 141 2006-09-11 04:51:07Z stonecrest $

import os, glob, shutil

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
		
os.system("intltool-merge -d -u   po mpdBrowser.desktop.in mpdBrowser.desktop")
# Create mo files:
if not os.path.exists("mo/"):
	os.mkdir("mo/")
for lang in ('de', 'pl', 'ru', 'fr', 'zh_CN', 'sv', 'es', 'fi', 'uk', 'it', 'cs', 'nl', 'pt_BR', 'da', 'be@latin'):
	pofile = "po/" + lang + ".po"
	mofile = "mo/" + lang + "/mpdBrowser.mo"
	if not os.path.exists("mo/" + lang + "/"):
		os.mkdir("mo/" + lang + "/")
	print "generating", mofile
	os.system("msgfmt %s -o %s" % (pofile, mofile))

setup(name='mpdBrowser',
        version='0.9.0',
        description='GTK+ client for the Music Player Daemon (MPD).',
        author='Bellegarde Cedric',
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
        data_files=[('share/mpdbrowser', ['README', 'CHANGELOG', 'TODO', 'TRANSLATORS']),
                    ('share/applications', ['mpdBrowser.desktop']),
                    ('share/locale/fr/LC_MESSAGES', ['mo/fr/mpdBrowser.mo']),
                    ('share/locale/it/LC_MESSAGES', ['mo/it/mpdBrowser.mo']),
                    ('share/locale/pl/LC_MESSAGES', ['mo/pl/mpdBrowser.mo']),
                    ('share/pixmaps', glob.glob('images/*'))],
        )

# Cleanup (remove /build, /mo, and *.pyc files:
print "Cleaning up..."
try:
	removeall("build/")
	os.rmdir("build/")
	removeall("mo/")
	os.rmdir("mo/")
	os.unlink("mpdBrowser.desktop")
except:
	pass
try:
	for f in os.listdir("."):
		if os.path.isfile(f):
			if os.path.splitext(os.path.basename(f))[1] == ".pyc":
				os.remove(f)
except:
	pass
