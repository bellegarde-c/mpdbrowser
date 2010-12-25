#!/bin/bash

if [ -n "$1" ] 
then
    prefix="$1"
else
    prefix=/usr
fi

cp -ax src orig
sed -i "s!@SYS@!$prefix!g" src/*.py src/mpdBrowser
python ./.setup.py install --prefix="$prefix"
rm -fr src
mv orig src
