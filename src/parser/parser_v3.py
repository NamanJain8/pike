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


myout = ""

class Node:
	def __init__(self, children=None, leaf=None):
		if children:
			self.children = children
		else:
			self.children = None
		self.leaf = leaf

def gendot(x, parent):
	global myout
	global ctr

	if x.children == None:
		return
	for i in x.children:
		if i == None:
			continue
		myout += str(ctr) + ' [label="' + i.leaf + '"];\n'
		myout += str(parent) +  ' -> ' + str(ctr) + ';\n'
		ctr += 1
		gendot(i,ctr-1)


def p_SourceFile(p):
	'SourceFile : PackageClause SEMICOLON ImportDeclList TopLevelDeclList '
	p[0] = Node([p[1],p[3],p[4]],'SourceFile')

def p_ImportDeclList(p):
	'''ImportDeclList : empty
				| ImportDeclList ImportDecl SEMICOLON '''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[2]],'ImportDeclList')

def p_TopLevelDecList(p):
	'''TopLevelDeclList : empty
				| TopLevelDeclList TopLevelDecl SEMICOLON '''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[2]], 'TopLevelDecl')




def p_PackageClause(p):
	'PackageClause  : PACKAGE IDENT'
	p[0] = Node([],'package: ' + p[1] )

def p_TopLevelDecl(p):
	'''TopLevelDecl  : Declaration
				| FunctionDecl
				| MethodDecl '''
	p[0] = Node([p[1]], 'TopLevelDecl')



def p_ImportDecl(p):
	'ImportDecl  : IMPORT ImportSpecTopList'
	p[1] = Node([],'import')
	p[0] = Node([p[1],p[2]],'ImportDecl')

def p_ImportSpecTopList(p):
	'''ImportSpecTopList : ImportSpec
			| LPAREN ImportSpecList RPAREN '''
	if p[1] == "(":
		p[0] = Node([p[2]], 'ImportSpecList')
	else:
		p[0] = Node([p[1]], 'ImportSpecList')

def p_ImportSpecList(p):
	'''ImportSpecList : empty
				| ImportSpecList ImportSpec SEMICOLON'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[2]],'ImportSpecList')

def p_ImportSpec(p):
	'ImportSpec  :  ImportSpecInit ImportPath '
	p[0] = Node([p[1],p[2]],'ImportSpec')

def p_ImportSpecInit(p):
	'''ImportSpecInit : empty
			| PERIOD
			| IDENT '''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([], 'ImportSpecList: ' + p[1])

def p_ImportPath(t):
	'ImportPath  : STRING '
	p[0] = Node([],"ImportPath: " + p[1])



def p_Block(p):
	'Block : LBRACE StatementList RBRACE'
	p[0] = Node([p[1]], "Block")

def p_StatementList(p):
	'''StatementList : empty
				| StatementList Statement SEMICOLON'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[2]],'StatementList')

def p_Statement(p):
	'''Statement : Declaration
				| SimpleStmt
				| ReturnStmt
				| Block
				| IfStmt
				| SwitchStmt
				| ForStmt '''
	p[0] = Node([p[1]], 'Statement')



def p_Declaration(p):
	'''Declaration  : ConstDecl
					| TypeDecl
					| VarDecl '''
	p[0] = Node([p[1]], 'Declaration')



def p_ConstDecl(p):
	' ConstDecl      : CONST ConstSpecTopList '
	p[1] = Node([],"const")
	p[0] = Node([p[1],p[2]], "ConstDecl")

def p_ConstSpecTopList(p):
	'''ConstSpecTopList : ConstSpec
					| LPAREN ConstSpecList RPAREN'''
	if p[1] == '(':
		p[0] = Node([p[2]], 'ConstSpecTopList')

def p_ConstSpecList(p):
	'''ConstSpecList : empty
					| ConstSpecList ConstSpec SEMICOLON '''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[2]],'ConstSpecList')

def p_ConstSpec(p):
	'ConstSpec      : IdentifierList ConstSpecTail '
	p[0] = Node([p[1],p[2]],'ConstSpec')

def p_ConstSpecTail(p):
	'''ConstSpecTail : empty
					| TypeTop ASSIGN ExpressionList '''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[3]], "ConstSpecTail: " + ASSIGN)


def p_TypeTop(p):
	'''TypeTop : empty
				| Type '''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node(p[1],'TypeTop')









def p_IdentifierList(p):
	"IdentifierList : IDENT IdentifierBotList"
	p[1] = Node('identifier', [], p[1])
	p[0] = Node('identifierList', [p[1], p[2]])

def p_IdentifierBotList(p):
	'''IdentifierBotList : empty
						| IdentifierBotList COMMA IDENT'''
	if p[1] == "":
		p[0] = None
	else:
		p[3] = Node([], 'identifier:' + p[3])
		p[0] = Node([p[1], p[3]], 'IdentifierBotList')

def p_ExpressionList(p):
	"ExpressionList : Expression ExpressionBotList"
	p[0] = Node([p[1], p[2]], 'ExpressionList')

def p_ExpressionBotList(p):
	'''ExpressionBotList : empty
						| ExpressionBotList COMMA Expression'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1], p[2]], 'ExpressionBotList')

# Line 32, 33, 34 not required




def p_TypeDecl(p):
	"TypeDecl : TYPE TypeSpecTopList"
	p[1] = Node([], 'type')
	p[0] = Node([p[1], p[2]], 'TypeDecl')

def p_TypeSpecTopList(p):
	'''TypeSpecTopList : TypeSpec
						| LPAREN TypeSpecList RPAREN'''
	if p[1] == "(":
		p[0] = Node([p[2]], 'TypeSpecTopList')
	else:
		p[0] = Node([p[1]], 'TypeSpecTopList')

def p_TypeSpecList(p):
	'''TypeSpecList : empty
					| TypeSpecList TypeSpec SEMICOLON'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1], p[2]], 'TypeSpecList')

def p_TypeSpec(p):
	'''TypeSpec : AliasDecl
				| TypeDef'''
	p[0] = Node([p[1]], 'TypeSpec')

def p_AliasDecl(p):
	"AliasDecl : IDENT ASSIGN Type"
	p[1] = Node([], 'identifier: ' + p[1])
	p[2] = Node([], 'type: ' + p[2])
	p[0] = Node([p[1], p[2]], 'AliasDecl: ' + ASSIGN)

def p_TypeDef(p):
	"TypeDef : IDENT Type"
	p[1] = Node([], 'identifier: ' + p[1])
	p[2] = Node([], 'type: ' + p[2])
	p[0] = Node([p[1], p[2]], 'TypeDef')





def p_Type(p):
	'''Type : TypeName
			| TypeLit
			| LPAREN Type RPAREN'''
	if p[1] == '(':
		p[0] = Node([p[2]], 'Type')
	else:
		p[0] = Node([p[1]], 'Type')

def p_TypeName(p):
	'''TypeName  : identifier
				| QualifiedIdent'''
	p[0] = Node([p[1]], 'TypeName')

def p_QualifiedIdent(p):
	"QualifiedIdent : identifier PERIOD identifier"
	p[1] = Node([], 'identifier: ' + p[1])
	p[3] = Node([], 'identifier: ' + p[3])
	p[0] = ([p[1], p[3]], 'QualifiedIdent')

def p_TypeLit(p):
	'''TypeLit   : ArrayType
				| StructType
				| FunctionType'''
	p[0] = Node([p[1]], 'TypeLit')

def p_ArrayType(p):
	"ArrayType   : LBRACK ArrayLength RBRACK ElementType"
	p[0] = Node([p[1], p[2]], 'ArrayType')

def p_ArrayLength(p):
	"ArrayLength : Expression"
	p[0] = Node([p[1]], 'ArrayLength')

def p_ElementType(p):
	"ElementType : Type"
	p[0] = Node([p[1]], 'ElementType')

def p_StructType(p):
	"StructType    : STRUCT LBRACE FieldDeclList RBRACE"
	p[1] = Node([], 'struct')
	p[0] = Node([p[1], p[3]], 'StructType')

def p_FieldDeclList(p):
	'''FieldDeclList : empty
					| FieldDeclList FieldDecl SEMICOLON'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1], p[2]], 'FieldDeclList')

def p_FieldDecl(p):
	"FieldDecl     : FieldDeclHead TagTop"
	p[0] = Node([p[1], p[2]], 'FieldDecl')

def p_TagTop(p):
	'''TagTop : empty
			| Tag'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1]], 'TagTop')

def p_FieldDeclHead(p):
	'''FieldDeclHead : IdentifierList Type
						| EmbeddedField'''

def p_EmbeddedField(p):
	"EmbeddedField : starTop TypeName"
	p[0] = Node([p[1], p[2]], 'EmbeddedField')

def p_starTop(p):
	'''starTop : empty
				| MUL '''
	if p[1] = "":
		p[0] = None
	else:
		p[0] = Node([], 'starTop: ' + MUL)

def p_Tag(p):
	"Tag           : string_lit"
	p[0] = Node([p[1]], 'Tag')

def p_FunctionType(p):
	"FunctionType   : FUNC Signature"
	p[1] = Node([], p[1])
	p[0] = Node([p[1], p[2]], 'FunctionType')

def p_Signature(p):
	"Signature      : Parameters ResultTop"
	p[0] = Node([p[1], p[2]], 'Signature')


def p_ResultTop(p):
	'''ResultTop : empty
				| Result'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1]], 'ResultTop')

def p_Result(p):
	'''Result         : Parameters
						| Type'''
	p[0] = Node([p[1]], 'Result')

def p_Parameters(p):
	'''Parameters     : LPAREN ParameterListTop RPAREN'''
	p[0] = Node([p[1]], 'Parameters')

def p_ParameterListTop(p):
	'''ParameterListTop : empty
						| ParameterList commaTop'''
	if p[1] = "":
		p[0] = None
	else:
		p[0] = Node([p[1], p[2]], 'ParameterListTop')

def p_commaTop(p):
	'''commaTop : empty
				| COMMA'''
	if p[1] = "":
		p[0] = None
	else:
		p[0] = Node([], 'commaTop: ' + COMMA)

def p_ParameterList(p):
	'''ParameterList  : ParameterDecl ParameterDeclList'''
	p[0] = Node([p[1], p[2]], 'ParameterList')

def p_ParameterDeclList(p):
	'''ParameterDeclList : empty
						| ParameterDeclList COMMA ParameterDecl'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1], p[3]], 'ParameterDeclList')

def p_ParameterDecl(p):
	"ParameterDecl  : ParameterDeclHead tripledotTop Type"
	p[0] = Node([p[1], p[2], p[3]], 'ParameterDecl')

def p_tripledotTop(p):
	'''tripledotTop : empty
					| ELLIPSIS'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([], 'tripledotTop: ' + ELLIPSIS)

def p_ParameterDeclHead(p):
	'''ParameterDeclHead : empty
						| IdentifierList'''
	if p[1] == "":
		p[0] = None
	else:
		p[1] = Node([p[1]], 'ParameterDeclHead')



###############

def p_VarDecl(p):
	''' VarDecl     : VAR VarSpecTopList '''
	p[1] = Node([],"VAR")
	p[0] = Node([p[1],p[2]],'VarDecl')

def p_VarSpecTopList(p):
	'''VarSpecTopList : VarSpec
			| LPAREN VarSpecList RPAREN '''
	if p[1] == "(":
		p[0] = Node([p[2]],'VarSpecTopList')
	else:
		p[0] = Node([p[1]],'VarSpecTopList')


def p_VarSpecList(p):
	'''VarSpecList : empty
				| VarSpecList VarSpec SEMICOLON'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1],p[2]],'VarSpecList')

def p_VarSpec(p):
	'''VarSpec  : IdentifierList VarSpecTail '''
	p[0] = Nde([p[1],p[2]],'VarSpec')

def p_VarSpecTail(p):
	'''VarSpecTail : Type VarSpecMid
					| ASSIGN ExpressionList '''
	if p[1] == "=":
		p[1] = Node([],ASSIGN)
		p[0] = Node([p[1],p[2]],'VarSpecTail')
	else:
		p[0] = Node([p[1],p[2]],'VarSpecList')


def p_VarSpecMid(p):
	'''VarSpecMid : empty
			| ASSIGN ExpressionList '''
	if p[0] == "":
		p[0] = None
	else:
		p[1] = Node([],ASSIGN)
		p[0] = Node([p[1],p[2]],'VarSpecMid')


#############################

def p_FunctionDecl(p):
	''' FunctionDecl : FUNC FunctionName FunctionDeclTail '''
	p[1] = Node([],'FUNC')
	p[0] = Node([p[1],p[2],p[3]],'FunctionDecl')

def p_FunctionDeclTail(p):
	'''FunctionDeclTail : Function
				| Signature'''
	p[0] = Node([p[1]],'Function')

def p_FunctionName(p):
	'''FunctionName : IDENT'''
	p[0] = Node([], 'FunctionName: ' + p[1])

def p_Function(p):
	'''Function     : Signature FunctionBody '''
	p[0] = Node([p[1],p[2]], 'Function')

def p_FunctionBody(p):
	'''FunctionBody : Block '''
	p[0] = Node([p[1]],'FunctionBody')

###########

def p_MethodDecl(p):
	'''MethodDecl : FUNC Receiver MethodName FunctionDeclTail '''
	p[1] = Node([],'func')
	p[0] = Node([p[1],p[2],p[3],p[4]], 'MethodDecl')

def p_Receiver(p):
	'''Receiver   : Parameters '''
	p[0] = Node([p[1]],'Receiver')

##############

def p_SimpleStmt(p):
	'''SimpleStmt = ExpressionStmt | Assignment | ShortVarDecl '''
	p[0] = Node([p[1]],'SimpleStmt')

def p_ExpressionStmt(p):
	'''ExpressionStmt : Expression '''
	p[0] = Node([p[1]], 'ExpressionStmt')

def p_ShortVarDecl(p):
	'''ShortVarDecl : IdentifierList DEFINE ExpressionList '''
	p[0] = Node([p[1],p[2]],'ShortVarDecl: ' + DEFINE)

def p_Assignment(p):
	'''Assignment : ExpressionList assign_op ExpressionList '''
	p[0] = Node([p[1],p[2],p[3]], 'Assignment')

def p_assign_op(p):
	'''assign_op : addmul_op ASSIGN '''
	p[0] = Node([p[1],p[2]],'assign_op')

def p_addmul_op(p):
	'''addmul_op : empty
			| add_op
			| mul_op '''
	if p[1] == "":
		p[0] = None
	else
		p[0] = Node([p[1]],'addmul_op')

def p_IfStmt(p):
	'''IfStmt : IF SimpleStmtBot Expression Block elseBot '''
	p[1] = Node([],'if')
	p[0] = Node([p[1],p[2],p[3],p[4],p[5]],'IfStmt')

def p_SimpleStmtBot(p):
	'''SimpleStmtBot : empty
			| SimpleStmt SEMICOLON '''
	if p[1] == "":
		p[0] = None
	else:
		p[1] = Node([p[1]],'SimpleStmtBot')

def p_elseBot(p):
	'''elseBot : empty
			| ELSE elseTail '''
	if p[1] == "":
		p[0] = None
	else:
		p[1] = Node([],'else')
		p[0] = Node([p[1],p[2]],'elseBot')

def p_elseTail(p):
	'''elseTail : IfStmt
			| Block '''
	p[0] = Node([p[1]],'elseTail')

def p_SwitchStmt(p):
	'''SwitchStmt : ExprSwitchStmt '''
	p[0] = Node([p[1]],'SwitchStmt')

def p_ExprSwitchStmt(p):
	''' ExprSwitchStmt : SWITCH SimpleStmtBot ExpressionBot LBRACE ExprCaseClauseList RBRACE '''
	p[1] = Node([],'switch')
	p[0] = Node([p[1],p[2],p[3],p[5]], 'ExprSwitchStmt')

def p_ExprCaseClause(p):
	'''ExprCaseClause : ExprSwitchCase COLON StatementList '''
	p[0] = Node([p[1],p[3]],'ExprCaseClause')

def p_ExprSwitchCase(p):
	''' ExprSwitchCase : CASE ExpressionList
						| DEFAULT '''
	if p[1] == "case":
		p[1] = Node([],'case')
		p[0] = Node([p[1],p[2]],'ExprSwitchCase')
	else:
		p[1] = Node([],'default')
		p[0] = Node([p[1]],'ExprSwitchCase')

def p_ForStmt(p):
	'''ForStmt : FOR ExpressionBot Block '''
	p[1] = Node([],'for')
	p[0] = Node([p[1],p[2],p[3]],'ForStmt')

def p_ExpressionBot(p):
	'''ExpressionBot : empty
				| Expression '''
	if p[1]=="":
		p[0] = None
	else:
		p[0] = Node([p[1]],'ExpressionBot')







# After line 104

def p_ReturnStmt(p):
	"ReturnStmt : RETURN ExpressionListBot"
	p[1] = Node([], 'return')

def p_ExpressionListBot(p):
	'''ExpressionListBot : empty
						| ExpressionList'''
	if p[1] == "":
		p[0] = None
	else:
		p[0] = Node([p[1]], 'ExpressionListBot')





def p_Expression(p):
	'''Expression : UnaryExpr
					| Expression binary_op Expression'''
	# To be completed



def p_UnaryExpr(p):
	'''UnaryExpr  : PrimaryExpr
				| unary_op UnaryExpr'''
	# To be completed

def p_binary_op(p):
	'''binary_op  : LOR
					| LAND
					| rel_op
					| add_op
					| mul_op'''
	if p[1] == "||" or p[1] == "&&":
		p[0] = Node([], 'binary_op: ' + p[1])
	else:
		p[0] = Node([p[1]], 'binary_op')

def p_rel_op(p):
	'''rel_op     : EQL
					| NEQ
					| LSS
					| LEQ
					| GTR
					| GEQ'''
	p[0] = Node([], 'rel_op: ' + p[1])

def p_add_op(p):
	'''add_op     : ADD
					| SUB
					| OR
					| XOR'''
	p[0] = Node([], 'add_op: ' + p[1])

def p_mul_op(p):
	'''mul_op     : MUL
					| QUO
					| REM
					| SHL
					| SHR
					| AND
					| AND_NOT'''
	p[0] = Node([], 'mul_op: ' + p[1])

def p_unary_op(p):
	'''unary_op   : "+"
					| "-"
					| "!"
					| "^"
					| "*"
					| "&"
					| "<-"'''
	p[0] = Node([], 'unary_op: ' + p[1])


def p_PrimaryExpr(p):
	'''PrimaryExpr :
		Operand |
		PrimaryExpr Selector |
		PrimaryExpr Index |
		PrimaryExpr Arguments'''
	p[0] = Node([p[1]], 'PrimaryExpr')







def p_Operand(p):
	'''Operand     : Literal
					| OperandName
					| MethodExpr
					| LPAREN Expression RPAREN'''
	if p[1] == "(":
		p[0] = Node([p[2]], 'Operand')
	else:
		p[0] = Node([p[1]], 'Operand')

def p_Literal(p):
	'''Literal     : BasicLit
					| FunctionLit'''
	p[0] = Node([p[1]], 'Literal')

def p_BasicLit(p):
	'''BasicLit    : int_lit
					| float_lit
					| string_lit'''
	p[0] = Node([p[1]], 'BasicLit')


# 129 to 137 not required

def p_int_lit(p):
	'''int_lit             : INT'''
	p[0] = Node([], 'int_lit: ' + p[1])

def p_float_lit(p):
	'''float_lit             : FLOAT'''
	p[0] = Node([], 'float_lit: ' + p[1])


def p_string_lit(p):
	'''string_lit             : STRING'''
	p[0] = Node([], 'string_lit: ' + p[1])







def p_empty(p):
	"empty : "
	pass




# def p_ForLoop(p):
# 	"ForLoop : FOR LPAREN cond RPAREN LBRACE stmt RBRACE"
# 	p[0] = Node('forLoop', [p[3],p[6]],p[1])

# 	global myout
# 	global ctr

# 	gendot(p[0],ctr-1)
# 	out_file.write(myout)

def p_error(p):
	print("Error in parsing!")
	print("Error at: ", p.type)
	sys.exit()

# Build lexer
lexer = lex.lex()
# lexer.abcde = 0   # custom global varibales for lexer

# Read input file
in_file_location = "input.go"
in_file = open(in_file_location,'r')
out_file = open("output.dot","w")
out_file.write('strict digraph G {\n')

data = in_file.read()

# Iterate to get tokens
parser = yacc.yacc()
res = parser.parse(data)

out_file.write("}\n")
# Close file
out_file.close()
in_file.close()
