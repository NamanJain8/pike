from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc 
import json
import argparse
import sys

"""
CITE:
    Most of the token definations are taken from documentation
    of golang(go docs), and some from the token (go/token)
    package of golang: https://golang.org/src/go/token/token.go
"""

# reserved words in language
reserved = {
    'break'        :    'BREAK',
    'default'      :    'DEFAULT',
    'select'       :    'SELECT',
    'func'         :    'FUNC',
    'case'         :    'CASE',
    'interface'    :    'INTERFACE',
    'defer'        :    'DEFER',
    'go'           :    'GO',
    'struct'       :    'STRUCT',
    'goto'         :    'GOTO',
    'chan'         :    'CHAN',
    'else'         :    'ELSE',
    'map'          :    'MAP',
    'fallthrough'  :    'FALLTHROUGH',
    'package'      :    'PACKAGE',
    'switch'       :    'SWITCH',
    'const'        :    'CONST',
    'range'        :    'RANGE',
    'type'         :    'TYPE',
    'if'           :    'IF',
    'continue'     :    'CONTINUE',
    'return'       :    'RETURN',
    'for'          :    'FOR',
    'import'       :    'IMPORT',
    'var'          :    'VAR',
}


# token list (compulsary)
tokens = [
    # literals
    'IDENT',            # main
    'INT',              # 123
    'FLOAT',            # 123.4
    'IMAG',             # 123.4i
    'CHAR',             # 'a'
    'STRING',           # "abc"

    # operator
    'ADD',              # +
    'SUB',              # -
    'MUL',              # *
    'QUO',              # /
    'REM',              # %

    'ADD_ASSIGN',       # +=
    'SUB_ASSIGN',       # -=
    'MUL_ASSIGN',       # *=
    'QUO_ASSIGN',       # %=
    'REM_ASSIGN',       # %=

    # bitwise operators
    'AND',              # &
    'OR',               # |
    'XOR',              # ^
    'SHL',              # <<
    'SHR',              # >>
    'AND_NOT',          # &^

    'AND_ASSIGN',       # &=
    'OR_ASSIGN',        # |=
    'XOR_ASSIGN',       # ^=
    'SHL_ASSIGN',       # <<=
    'SHR_ASSIGN',       # >>=
    'AND_NOT_ASSIGN',   # &^=

    'LAND',             # &&
    'LOR',              # ||
    'ARROW',            # <-
    'INC',              # ++
    'DEC',              # --

    'EQL',              # ==
    'LSS',              # <
    'GTR',              # >
    'ASSIGN',           # =
    'NOT',              # !

    'NEQ',              # !=
    'LEQ',              # <=
    'GEQ',              # >=
    'DEFINE',           # :=
    'ELLIPSIS',         # ...

    'LPAREN',           # (
    'LBRACK',           # [
    'LBRACE',           # {
    'COMMA',            # ,
    'PERIOD',           # .

    'RPAREN',           # )
    'RBRACK',           # ]
    'RBRACE',           # }
    'SEMICOLON',        # ;
    'COLON',            # :

] + list(reserved.values())

# Mathematical operators
t_ADD   = r"\+"
t_SUB   = r"-"
t_MUL   = r"\*"
t_QUO   = r"/"
t_REM   = r"%"

t_ADD_ASSIGN    = r"\+="
t_SUB_ASSIGN    = r"-="
t_MUL_ASSIGN    = r"\*="
t_QUO_ASSIGN    = r"/="
t_REM_ASSIGN    = r"%="

# bitwise operators
t_AND   = r"&"
t_OR    = r"\|"
t_XOR   = r"\^"
t_SHL   = r"<<"
t_SHR   = r">>"
t_AND_NOT   = r"&\^"

AND_ASSIGN  = r"&="
OR_ASSIGN   = r"!="
XOR_ASSIGN  = r"\^="
SHL_ASSIGN  = r"<<="
SHR_ASSIGN  = r">>="
AND_NOT_ASSIGN  = r"&\^="

t_LAND  = r"&&"
t_LOR   = r"\|\|"
t_ARROW = r"<-"
t_INC   = r"\+\+"
t_DEC   = r"--"

t_EQL   = r"=="
t_LSS   = r"<"
t_GTR   = r">"
t_ASSIGN    = r"="
t_NOT   = "!"

t_NEQ   = r"!="
t_LEQ   = r"<="
t_GEQ   = r">="
t_DEFINE    = r":="
t_ELLIPSIS  = r"\.\.\."

t_LPAREN    = r"\("
t_LBRACK    = r"\["
t_LBRACE    = r"\{"
t_COMMA     = r","
t_PERIOD    = r"\."

t_RPAREN    = r"\)"
t_RBRACK    = r"\]"
t_RBRACE    = r"\}"
t_SEMICOLON = r";"
t_COLON     = r":"

letter = r"[_A-Za-z]"
decimal_digit   = r"[0-9]"
octal_digit = r"[0-7]"
hexa_digit  = r"[0-9a-fA-F]"

identifier = letter + r"(" + letter + r"|" + decimal_digit + r")*"

octal_literal = r"0[0-7]*"
hexa_literal = r"0[xX][0-9a-fA-F]+"
decimal_literal = r"[1-9][0-9]*"
t_INT   = decimal_literal + r"|" + octal_literal + r"|" + hexa_literal

decimals = decimal_digit + r"(" + decimal_digit + r")*"
exponent = r"(e|E)" + r"(\+|-)?" + decimals
t_FLOAT = r"(" + decimals + r"\." + decimals + exponent + r")|(" + decimals + exponent + r")|(" + r"\." + decimals + exponent + r")"

t_IMAG  = r"(" + decimals + r"|" + t_FLOAT + r")" + r"i"

t_ignore = " \t"

# t_STRING = r"\"[.]+\""
ctr = 1
# Definig functions for each token

@TOKEN(identifier)
def t_IDENT(t):
    t.type = reserved.get(t.value,"IDENT")
    return t

def t_NL(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    pass

def t_COMMENT(t):
    r"(//.*)|(/\*(.|\n)*?)\*/"
    pass

def t_STRING(t):
    r"(\"(.|\n)*?)\""
    return t

def t_error(t):
    print("[ERROR] Invalid token:",t.value[0])
    t.lexer.skip(1) #skip ahead 1 character


def p_ForLoop(p):
	"ForLoop : e_for FOR LPAREN a_cond cond RPAREN LBRACE a_stmt stmt RBRACE"

def p_e_for(p):
	"e_for : "
	global ctr
	p[0] = ctr

	out_file.write(str(ctr+1) + ' [label="FOR"];\n')
	out_file.write(str(ctr+2) + ' [label="LPAREN"];\n')
	out_file.write(str(ctr+3) + ' [label="cond"];\n')
	out_file.write(str(ctr+4) + ' [label="RPAREN"];\n')
	out_file.write(str(ctr+5) + ' [label="LBRACE"];\n')
	out_file.write(str(ctr+6) + ' [label="stmt"];\n')
	out_file.write(str(ctr+7) + ' [label="RBRACE"];\n')

	out_file.write(str(ctr) + ' -> ' + str(ctr+1) + ';\n')
	out_file.write(str(ctr) + ' -> ' + str(ctr+2) + ';\n')
	out_file.write(str(ctr) + ' -> ' + str(ctr+3) + ';\n')
	out_file.write(str(ctr) + ' -> ' + str(ctr+4) + ';\n')
	out_file.write(str(ctr) + ' -> ' + str(ctr+5) + ';\n')
	out_file.write(str(ctr) + ' -> ' + str(ctr+6) + ';\n')
	out_file.write(str(ctr) + ' -> ' + str(ctr+7) + ';\n')

	ctr += 7

def p_a_cond(p):
	"a_cond : "
	p[0] = p[-3] + 3
	# print("in cond: ", p[0])

def p_a_stmt(p):
	"a_stmt : "
	p[0] = p[-7] + 6

def p_cond(p):
	"cond : IDENT EQL INT"
	global ctr
	out_file.write(str(ctr+1) + '[label="' + p[1] + '"];\n')
	out_file.write(str(ctr+2) + '[label="' + p[2] + '"];\n')
	out_file.write(str(ctr+3) + '[label="' + p[3] + '"];\n')

	out_file.write(str(p[-1]) + ' -> ' + str(ctr+1) + ';\n')
	out_file.write(str(p[-1]) + ' -> ' + str(ctr+2) + ';\n')
	out_file.write(str(p[-1]) + ' -> ' + str(ctr+3) + ';\n')
	ctr += 3

def p_stmt(p):
	"stmt : IDENT ASSIGN IDENT SEMICOLON"
	global ctr
	out_file.write(str(ctr+1) + '[label="IDENT"];\n')
	out_file.write(str(ctr+2) + '[label="ASSIGN"];\n')
	out_file.write(str(ctr+3) + '[label="IDENT"];\n')
	out_file.write(str(ctr+4) + '[label="SEMICOLON"];\n')

	out_file.write(str(p[-1]) + ' -> ' + str(ctr+1) + ';\n')
	out_file.write(str(p[-1]) + ' -> ' + str(ctr+2) + ';\n')
	out_file.write(str(p[-1]) + ' -> ' + str(ctr+3) + ';\n')
	out_file.write(str(p[-1]) + ' -> ' + str(ctr+4) + ';\n')
	ctr += 4

def p_error(p):
	print("Error in parsing!")
	sys.exit()

# Build lexer
lexer = lex.lex()
# lexer.abcde = 0   # custom global varibales for lexer

# Read input file
in_file_location = "input.go"
in_file = open(in_file_location,'r')
out_file = open("output.dot","w")
out_file.write('strict digraph G {\n')
out_file.write(str(ctr) + ' [label="ForLoop"];\n')

data = in_file.read()

# Iterate to get tokens
parser = yacc.yacc()
res = parser.parse(data)

out_file.write("}\n")
# Close file
out_file.close()
in_file.close()

