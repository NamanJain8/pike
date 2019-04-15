#!/bin/bash

goFile=$1

python3 parser.py --input=$goFile --csv="symTab.csv" --code="3AC.code"
python3 codeGen.py

nasm -f elf32 "assembly.asm" -o "assembly.o"
gcc -m32 "assembly.o" -o "a.out"

rm -f "symTab.csv" "3AC.code" "assembly.asm" "assembly.o"
