#!/bin/bash

path=$PWD"/src/parser/"
test_path=$PWD"/tests/input2/"
out_path=$PWD"/tests/output2/"

for i in 1 2 3 4 5
do
   echo $i
   # cp $test_path"test"$i".go" $path"input.go"
   python3 $path"parser_v4.py" --input=$test_path"test"$i".go" --output=$out_path"out"$i".dot"
   dot -Tps $out_path"out"$i".dot" -o $out_path"out"$i".ps"
done
