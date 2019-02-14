#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

crontab -l > tmp_file
echo "*/5 * * * * bash $DIR/pull.sh" >> tmp_file
crontab tmp_file
rm tmp_file
