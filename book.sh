#!/bin/bash

pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

echo $(date) - Script Started
python  $SCRIPTPATH/book.py
echo $(date) - Script Finished
