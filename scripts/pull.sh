#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
present=`pwd`

cd $DIR
cd ..
git pull upstream master

cd $present
