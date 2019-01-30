Requirements: python3, ply and argparse package

RUNNING LEXER:
	$ python3 src/lexer/lexer.py --cfg=tests/cfg1/color2.json --output=tests/output/code.html --input=tests/input1/consistent_hashing.go

NOTE: input, output and config directory can be different from the above ones.
eg:
	$ python3 src/lexer/lexer.py --cfg=config/color3.json --output=golang.html --input=tests/input1/test1.go

