from ply import lex
from ply.lex import TOKEN
import sys
import json

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

# Regex defining
t_ignore_COMMENT = r'\#.*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EXPO = r'\*\*'
t_LBRAC = r'\('
t_RBRAC = r'\)'
t_EQUAL = r'='
t_ASSIGN = r'=='

digit = r'[0-9]'
nondigit = r'[_A-Za-z]'
identifier = r'(' + nondigit + r'(' + digit + r'|' + nondigit + r')*)'

# Definig functions for each token
@TOKEN(identifier)
def t_ID(t):
    data = "<font color=" + colors["ID"] + ">" + t.value + "</font>\n"
    out_file.write(data)
    return t

def t_NL(t):
    r'\n'
    out_file.write("\n")
    t.lexer.lineno += 1

def t_SPACE(t):
    r'\ '
    out_file.write("&nbsp;\n")
    return

def t_TAB(t):
    r'\t'
    out_file.write("&nbsp;&nbsp;&nbsp;&nbsp;")
    return

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_error(t):
    print("[ERROR] Invalid token:",t.value[0])
    t.lexer.skip(1) #skip ahead 1 character

# Build lexer
lexer = lex.lex()
# lexer.abcde = 0   # custom global varibales for lexer

# Load config file for colors
with open("../../config/color.json") as config:
    colors = json.load(config)
# print(colors["ID"])

# Open output file
out_file = open("output.html","w+")
out_file.write("<html>\n<body>\n")

# Read input file
in_file = open('input','r')
data = in_file.read()

lexer.input(data)

# Iterate to get tokens
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)

# Close file
in_file.close()
out_file.write("</body>\n</html>\n")
out_file.close()