#!/bin/bash

array=($(ls basic_tests))
a='basic_tests/'

echo "Basic Test Cases Running"

for goFile in "${array[@]}"
do
    echo ""
    echo "==================================="
    echo $a$goFile
    python3 parser.py --input=$a$goFile --csv="symTab.csv" --code="3AC.code"
    python3 codeGen.py

    nasm -f elf32 "assembly.asm" -o "assembly.o"
    gcc -m32 "assembly.o" -o "a.out"
    ./a.out

    # rm -f "symTab.csv" "3AC.code" "assembly.asm" "assembly.o"
    rm -f "symTab.csv" "3AC.code" "assembly.o"
   # or do whatever with individual element of the array
done

# python3 parser.py --input=$goFile --csv="symTab.csv" --code="3AC.code"
# python3 codeGen.py
#
# nasm -f elf32 "assembly.asm" -o "assembly.o"
# gcc -m32 "assembly.o" -o "a.out"
#
# rm -f "symTab.csv" "3AC.code" "assembly.asm" "assembly.o"
