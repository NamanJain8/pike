#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pwd=`pwd`

cd $DIR
cd ".."

# delete html files
find . -type f -iname "*.html" -delete

# delete all executables.
find . -type f -iname "*.o" -delete

# delete all pycache directories
find . -type d -iname "__pycache__" -exec rm -rf "{}" \;

rm -f "bin/default_dot" "bin/default_html"

cd $pwd