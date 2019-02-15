Requirements: python3, ply and argparse package

RUNNING PARSER:
	$ python3 src/parser/parser_final.py --output=tests/output2/out1.dot --input=tests/input2/test1.go
	$ dot -Tps tests/output2/out1.dot tests/output2/out1.ps

NOTE: input, output and config directory can be different from the above ones.
eg:
	$ python3 src/parser/parser_final.py --output=out.dot --input=tests/input2/test1.go

But, you can run all the 10 test cases (all the 10 .go files present in /tests/input2) using the Makefile present in the Main Assignment Directory.

Just Navigate to the main assignment directory and execute the commands:

```
make
make clean
```

[The first command is not mandatory but it is useful as it would remove the ___pycache___ folder from the `src/parser` directory and would also delete the previously created out1.dot, out2.dot etc. and out1.ps, out2.ps etc.]

The output files (.dot files and converted .ps files) will be stored in /tests/output2 folder
