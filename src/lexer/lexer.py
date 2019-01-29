from ply import lex
from ply.lex import TOKEN
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

# t_STRING = r"\"[.]+\""

# Definig functions for each token
@TOKEN(identifier)
def t_IDENT(t):
    t.type = reserved.get(t.value,"IDENT")
    return t

def t_STRING(t):
    r"(\"(.|\n)*?)\""
    return t

def t_TAB(t):
    r"\t"
    data = "&nbsp;&nbsp;&nbsp;&nbsp;"
    out_file.write(data)
    pass

def t_NL(t):
    r"\n+"
    data = "<br>"*len(t.value)
    t.lexer.lineno += len(t.value)
    out_file.write(data)
    pass

def t_SPACE(t):
    r"\ "
    data = "&nbsp;"
    out_file.write(data)
    pass

def t_COMMENT(t):
    r"(//.*)|(/\*(.|\n)*?)\*/"
    data = "<font color=" + colors.get(t.type,"BLACK") + ">" + t.value + "</font>\n"
    out_file.write(data)
    pass


def t_error(t):
    print("[ERROR] Invalid token:",t.value[0])
    t.lexer.skip(1) #skip ahead 1 character


# Build lexer
lexer = lex.lex()
# lexer.abcde = 0   # custom global varibales for lexer

# Load config file for colors
with open("../../config/color3.json") as config:
    colors = json.load(config)
# print(colors["ID"])

# Open output file
out_file = open("../../tests/output.html","w+")
out_file.write("<html>\n<body bgcolor=" + colors.get("BODY","#x000000") + ">\n")

# Read input file
in_file = open('../../tests/input1.go','r')
data = in_file.read()

lexer.input(data)
ignored_tokens = ["COMMENT","NL","SPACE","TAB"]

# Iterate to get tokens
while True:
    tok = lexer.token()
    if not tok:
        break
    if tok.type in ignored_tokens:
        continue
    if tok.type in reserved.values():
        out_file.write("<b>")
    data = "<font color=" + colors[tok.type] + ">" + tok.value + "</font>\n"
    out_file.write(data) 
    if tok.type in reserved.values():
        out_file.write("</b>")
    print(tok)

# Close file
in_file.close()
out_file.write("</body>\n</html>\n")
out_file.close()
