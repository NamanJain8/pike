# Pike: Go Compiler
Compiler Design Project (Golang to X86 compiler written in Python3)

|       Name      | Roll No |        Email        |
|:---------------:|:-------:|:-------------------:|
| Devanshu Somani |  160231 | devanshu@iitk.ac.in |
|    Naman Jain   |  160427 |  namanj@iitk.ac.in  |
|  Raghukul Raman |  160538 | raghukul@iitk.ac.in |

## Features:
### Basic features:
- Native data types: Int, Char, Float
- Variables and Expressions
- Conditional: if, if-else
- Loops: for
- Break, Continue
- Arrays: Single and multidimensional
- Input, output
- Functions, recursion
- Pointers: Single and multilevel
- Simple library functions
- Arithmetic operators
- Logical and bitwise operators
- Multiple assignments in single line (a, b, c := 1,2,3)
- Thorough type checking

### Additional features
- Function overloading
- Auto-type inference
- Short variable declaration
- Alias, typedefs
- Structural equivalence
- Global variables
- Array returning from functions


<!-- Note: Before pushing run `clean.sh` to delete tmp files. -->

## Running the Parser
Navigate to this directory and execute the following command in the terminal:

```
make
make clean
```

*The first command is not mandatory but it is useful as it would remove the ___pycache___ folder from the `src/parser` directory and would also delete the previously created out1.dot, out2.dot etc. and out1.ps, out2.ps etc.*

This will take 10 input `.go` files from the `tests/input2` and will create 10 corresponding `.dot` and `.ps` files in the `tests/output2` directory.

Project Completed..
Updated again!
