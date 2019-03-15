Run using
	$ python3 src/parser.py --input=path_to_input --code=name_of_code_file --csv=name_of_sym_table_csv

If you want to debug, add --debug=True

In test directory there are 4 sub directories
	1. input
		contain sample working programs.
	2. buggy_codes
		contain sample buggy programs(having semantic errors).

	3. output
		contain symbol table and code for all the files of input directory above.
	4. error_msgs
		contains the error message for buggy programs of semantic_error dir codes.

