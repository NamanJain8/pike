#!/bin/bash

path=$PWD"/src/parser/"
test_path=$PWD"/tests/input2/"
out_path=$PWD"/tests/output2/"

for i in 1 2 3 4 5 6 7 8 9 10
do
   echo "Parsing and converting test"$i".go into its corresponding out"$i".dot and out"$i".ps"
   # cp $test_path"test"$i".go" $path"input.go"
   python3 $path"parser_final.py" --input=$test_path"test"$i".go" --output=$out_path"out"$i".dot"
   dot -Tps $out_path"out"$i".dot" -o $out_path"out"$i".ps"
done
