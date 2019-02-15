from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc
import json
import argparse
import sys

## uncomment this for debugging

# def tracefunc(frame, event, arg, indent=[0]):
# 	  if event == "call":
# 		  indent[0] += 2
# 		  print ("-" * indent[0] + "> call function", frame.f_code.co_name)
# 	  elif event == "return":
# 		  print ("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
# 		  indent[0] -= 2
# 	  return tracefunc
#
# sys.settrace(tracefunc)


"""
CITE:
  Most of the token definations are taken from documentation
  of golang(go docs), and some from the token (go/token)
  package of golang: https://golang.org/src/go/token/token.go
"""

# reserved words in language
reserved = {
	'break':    'BREAK',
	'default':    'DEFAULT',
	'select':    'SELECT',
	'func':    'FUNC',
	'case':    'CASE',
	'interface':    'INTERFACE',
	'defer':    'DEFER',
	'go':    'GO',
	'struct':    'STRUCT',
	'goto':    'GOTO',
	'chan':    'CHAN',
	'else':    'ELSE',
	'map':    'MAP',
	'fallthrough':    'FALLTHROUGH',
	'package':    'PACKAGE',
	'switch':    'SWITCH',
	'const':    'CONST',
	'range':    'RANGE',
	'type':    'TYPE',
	'if':    'IF',
	'continue':    'CONTINUE',
	'return':    'RETURN',
	'for':    'FOR',
	'import':    'IMPORT',
	'var':    'VAR',
	'int': 'INT',
	'float': 'FLOAT',
	'string': 'STRING',
	'bool': 'BOOL',
	'complex': 'COMPLEX',
	'typecast': 'TYPECAST'
}


# token list (compulsary)
tokens = [
	# literals
	'IDENT',            # main
	'INT_LITERAL',              # 123
	'FLOAT_LITERAL',            # 123.4
	'IMAG',             # 123.4i
	'CHAR',             # 'a'
	'STRING_LITERAL',           # "abc"

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
t_ADD = r"\+"
t_SUB = r"-"
t_MUL = r"\*"
t_QUO = r"/"
t_REM = r"%"

t_ADD_ASSIGN = r"\+="
t_SUB_ASSIGN = r"-="
t_MUL_ASSIGN = r"\*="
t_QUO_ASSIGN = r"/="
t_REM_ASSIGN = r"%="

# bitwise operators
t_AND = r"&"
t_OR = r"\|"
t_XOR = r"\^"
t_SHL = r"<<"
t_SHR = r">>"
t_AND_NOT = r"&\^"

AND_ASSIGN = r"&="
OR_ASSIGN = r"!="
XOR_ASSIGN = r"\^="
SHL_ASSIGN = r"<<="
SHR_ASSIGN = r">>="
AND_NOT_ASSIGN = r"&\^="

t_LAND = r"&&"
t_LOR = r"\|\|"
t_ARROW = r"<-"
t_INC = r"\+\+"
t_DEC = r"--"

t_EQL = r"=="
t_LSS = r"<"
t_GTR = r">"
t_ASSIGN = r"="
t_NOT = "!"

t_NEQ = r"!="
t_LEQ = r"<="
t_GEQ = r">="
t_DEFINE = r":="
t_ELLIPSIS = r"\.\.\."

t_LPAREN = r"\("
t_LBRACK = r"\["
t_LBRACE = r"\{"
t_COMMA = r","
t_PERIOD = r"\."

t_RPAREN = r"\)"
t_RBRACK = r"\]"
t_RBRACE = r"\}"
t_SEMICOLON = r";"
t_COLON = r":"

letter = r"[_A-Za-z]"
decimal_digit = r"[0-9]"
octal_digit = r"[0-7]"
hexa_digit = r"[0-9a-fA-F]"

identifier = letter + r"(" + letter + r"|" + decimal_digit + r")*"

octal_literal = r"0[0-7]*"
hexa_literal = r"0[xX][0-9a-fA-F]+"
decimal_literal = r"[1-9][0-9]*"
t_INT_LITERAL = decimal_literal + r"|" + octal_literal + r"|" + hexa_literal

decimals = decimal_digit + r"(" + decimal_digit + r")*"
exponent = r"(e|E)" + r"(\+|-)?" + decimals
t_FLOAT_LITERAL = r"(" + decimals + r"\." + decimals + exponent + r")|(" + \
	decimals + exponent + r")|(" + r"\." + decimals + exponent + r")"

t_IMAG = r"(" + decimals + r"|" + t_FLOAT_LITERAL + r")" + r"i"

t_ignore = " \t"

# t_STRING_LITERAL = r"\"[.]+\""
ctr = 1
# Definig functions for each token


@TOKEN(identifier)
def t_IDENT(t):
	t.type = reserved.get(t.value, "IDENT")
	return t


def t_NL(t):
	r"\n+"
	t.lexer.lineno += len(t.value)
	pass


def t_COMMENT(t):
	r"(//.*)|(/\*(.|\n)*?)\*/"
	pass


def t_STRING_LITERAL(t):
	r"(\"(.|\n)*?)\""
	return t


def t_error(t):
	print("[ERROR] Invalid token:", t.value[0])
	t.lexer.skip(1)  # skip ahead 1 character


myout = ""


class Node:
	def __init__(self, leaf="", children=[]):
		if children:
			self.children = children
		else:
			self.children = None
		self.leaf = leaf
		self.parent = 0
		self.valid = True

def pre(node, parent):
	if node.children == None:
		return
	global ctr
	for i in node.children:
		if i == None:
			continue
		ctr += 1
		# print(i)
		i.parent = parent
		pre(i, ctr - 1)
	return node

def pre2(node):
	if node.children == None:
		return
	count = 0
	for i in node.children:
		if i != None:
			count += 1
	if count == 1:
		node.valid = False
	for child in node.children:
		if child != None:
			if count == 1:
				child.parent = node.parent
			pre2(child)

	return node


def gendot(x, parent):
	global myout
	global ctr

	if x.children == None:
		return
	for i in x.children:
		if i == None:
			continue
		if i.valid:
			myout += str(ctr) + ' [label="' + (i.leaf).replace('"','') + '"];\n'
			myout += str(i.parent) + ' -> ' + str(ctr) + ';\n'
		ctr += 1
		gendot(i, ctr - 1)


precedence = (
	('right', 'ASSIGN', 'NOT'),
	('left', 'LOR'),
	('left', 'LAND'),
	('left', 'OR'),
	('left', 'XOR'),
	('left', 'AND'),
	('left', 'EQL', 'NEQ'),
	('left', 'LSS', 'GTR', 'LEQ', 'GEQ'),
	('left', 'SHL', 'SHR'),
	('left', 'ADD', 'SUB'),
	('left', 'MUL', 'QUO', 'REM'),
)

# ------------------------START----------------------------


def p_start(p):
	'''start : SourceFile'''
	global ctr
	global myout
	p[0] = Node("start", [p[1]])

	p[0] = pre(p[0], 0)
	p[0] = pre2(p[0])
	ctr = 1
	gendot(p[0],ctr-1)
	out_file.write(myout)
# -------------------------------------------------------


# -----------------------TYPES---------------------------
def p_type(p):
	'''Type : TypeName
					| TypeLit
					| LPAREN Type RPAREN'''
	if len(p) == 4:
		# p[1] = Node(p[1])
		# p[3] = Node(p[3])
		# p[0] = Node("Type",[p[1],p[2],p[3]])
		p[0] = Node("Type",[p[2]])
	else:
		p[0] = Node("Type",[p[1]])


def p_type_name(p):
	'''TypeName : TypeToken
							| QualifiedIdent'''
	p[0] = Node("TypeName",[p[1]])


def p_type_token(p):
	'''TypeToken : INT
							 | FLOAT
							 | STRING
							 | BOOL
							 | COMPLEX
							 | TYPE IDENT'''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[2] = Node(p[2])
		p[0] = Node("TypeToken", [p[1],p[2]])
	else:
		p[1] = Node(p[1])
		p[0] = Node("TypeToken", [p[1]])


def p_type_lit(p):
	'''TypeLit : ArrayType
					   | StructType
					   | PointerType'''
	p[0] = Node("TypeLit",[p[1]])


def p_type_opt(p):
	'''TypeOpt : Type
					   | epsilon'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("TypeOpt", [p[1]])
# -------------------------------------------------------


# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
	'''ArrayType : LBRACK ArrayLength RBRACK ElementType'''
	# p[1] = Node(p[1])
	# p[3] = Node(p[3])
	# p[0] = Node("ArrayType", [p[1],p[2],p[3],p[4]])
	p[0] = Node("ArrayType", [p[2], p[4]])


def p_array_length(p):
	''' ArrayLength : Expression '''
	p[0] = Node("ArrayLength", [p[1]])


def p_element_type(p):
	''' ElementType : Type '''
	p[0] = Node("ElementType", [p[1]])

# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
	'''StructType : STRUCT LBRACE FieldDeclRep RBRACE'''
	p[1] = Node(p[1])
	# p[2] = Node(p[2])
	# p[4] = Node(p[4])
	# p[0] = Node("StructType", [p[1],p[2],p[3],p[4]])
	p[0] = Node("StructType", [p[1], p[3]])


def p_field_decl_rep(p):
	''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
									| epsilon '''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("FieldDecl", [p[1],p[2],p[3]])
		p[0] = Node("FieldDecl", [p[1],p[2]])
	else:
		p[0] = None


def p_field_decl(p):
	''' FieldDecl : IdentifierList Type TagOpt'''
	p[0] = Node("FieldDecl", [p[1],p[2],p[3]])


def p_TagOpt(p):
	''' TagOpt : Tag
				| epsilon '''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("TagOpt", [p[1]])


def p_Tag(p):
	''' Tag : STRING_LITERAL '''
	p[1] = Node(p[1])
	p[0] = Node("Tag", [p[1]])
# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
	'''PointerType : MUL BaseType'''
	p[1] = Node("*")
	p[0] = Node("PointerType", [p[1], p[2]])


def p_base_type(p):
	'''BaseType : Type'''
	p[0] = Node("BaseType", [p[1]])
# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
	'''Signature : Parameters ResultOpt'''
	p[0] = Node("Signature", [p[1], p[2]])


def p_result_opt(p):
	'''ResultOpt : Result
							 | epsilon'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("ResultTop", [p[1]])


def p_result(p):
	'''Result : Parameters
					  | Type'''
	p[0] = Node("Result", [p[1]])


def p_params(p):
	'''Parameters : LPAREN ParameterListOpt RPAREN'''
	# p[1] = Node("(")
	# p[3] = Node(")")
	# p[0] = Node("Parameters", [p[1], p[2], p[3]])
	p[0] = Node("Parameters", [p[2]])


def p_param_list_opt(p):
	'''ParameterListOpt : ParametersList
													 | epsilon'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("ParameterListOpt", [p[1]])


def p_param_list(p):
	'''ParametersList : Type
									  | IdentifierList Type
									  | ParameterDeclCommaRep'''
	if len(p) == 3:
		p[0] = Node("ParameterList", [p[1], p[2]])
	else:
		p[0] = Node("ParameterList", [p[0]])


def p_param_decl_comma_rep(p):
	'''ParameterDeclCommaRep : ParameterDeclCommaRep COMMA ParameterDecl
													 | ParameterDecl COMMA ParameterDecl'''
	p[2] = Node(",")
	p[0] = Node("ParameterDeclCommaRep", [p[1], p[2], p[3]])


def p_param_decl(p):
	'''ParameterDecl : IdentifierList Type
									 | Type'''
	if len(p) == 3:
		p[0] = Node("ParameterDecl", [p[1], p[2]])
	else:
		p[0] = Node("ParameterDecl", [p[1]])
# ---------------------------------------------------------


# -----------------------BLOCKS---------------------------
def p_block(p):
	'''Block : LBRACE StatementList RBRACE'''
	# p[1] = Node("{")
	# if p[2] != None:
	# 	p[2] = Node("StatementList",p[2].children)
	# p[3] = Node("}")
	# p[0] = Node("Block", [p[1], p[2], p[3]])
	p[0] = Node("Block", [p[2]])


def p_stat_list(p):
	'''StatementList : StatementRep'''
	# p[0] = Node("StatementList", [p[1]])
	p[0] = p[1]


def p_stat_rep(p):
	'''StatementRep : StatementRep Statement SEMICOLON
									| epsilon'''
	if len(p) == 4:
		# p[3] = Node(";")
		# p[0] = Node("StatementRep", [p[1], p[2], p[3]])
		mylist = []
		if p[1] != None:
			mylist.extend(p[1].children)
		mylist.append(p[2])
		p[0] = Node("StatementRep",mylist)
	else:
		p[0] = None
# -------------------------------------------------------


# ------------------DECLARATIONS and SCOPE------------------------
def p_decl(p):
	'''Declaration : ConstDecl
								   | TypeDecl
								   | VarDecl'''
	p[0] = Node("Declaration", [p[1]])


def p_toplevel_decl(p):
	'''TopLevelDecl : Declaration
									| FunctionDecl'''
	p[0] = Node("TopLevelDecl", [p[1]])
# -------------------------------------------------------


# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
	'''ConstDecl : CONST ConstSpec
							 | CONST LPAREN ConstSpecRep RPAREN'''
	p[1] = Node(p[1])
	if len(p) == 3:
		p[0] = Node("ConstDecl", [p[1], p[2]])
	else:
		# p[2] = Node(p[2])
		# p[4] = Node(p[4])
		# p[0] = Node("ConstDecl", [p[1], p[2], p[3], p[4]])
		p[0] = Node("ConstDecl", [p[1], p[3]])


def p_const_spec_rep(p):
	'''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
									| epsilon'''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("ConstSpecRep", [p[1], p[2], p[3]])
		p[0] = Node("ConstSpecRep", [p[1], p[2]])
	else:
		p[0] = None


def p_const_spec(p):
	'''ConstSpec : IdentifierList TypeExprListOpt'''
	p[0] = Node("ConstSpec", [p[1], p[2]])


def p_type_expr_list(p):
	'''TypeExprListOpt : TypeOpt ASSIGN ExpressionList
									   | epsilon'''
	if len(p) == 4:
		p[2] = Node(p[2])
		p[0] = Node("TypeExprListOpt", [p[1], p[2], p[3]])
	else:
		p[0] = None


def p_identifier_list(p):
	'''IdentifierList : IDENT IdentifierRep'''
	p[1] = Node(p[1])
	p[0] = Node("IdentifierList", [p[1], p[2]])


def p_identifier_rep(p):
	'''IdentifierRep : IdentifierRep COMMA IDENT
									 | epsilon'''
	if len(p) == 4:
		p[2] = Node(p[2])
		p[3] = Node(p[3])
		p[0] = Node("IdentifierRep", [p[1], p[2], p[3]])
	else:
		p[0] = None


def p_expr_list(p):
	'''ExpressionList : Expression ExpressionRep'''
	p[0] = Node("ExpressionList", [p[1], p[2]])


def p_expr_rep(p):
	'''ExpressionRep : ExpressionRep COMMA Expression
									 | epsilon'''
	if len(p) == 4:
		p[2] = Node(p[2])
		p[0] = Node("ExpressionRep", [p[1], p[2], p[3]])
	else:
		p[0] = None
# -------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
	'''TypeDecl : TYPE TypeSpec
							| TYPE LPAREN TypeSpecRep RPAREN'''
	if len(p) == 5:
		p[1] = Node(p[1])
		# p[2] = Node(p[2])
		# p[4] = Node(p[4])
		# p[0] = Node("TypeDecl", [p[1],p[2],p[3],p[4]])
		p[0] = Node("TypeDecl", [p[1], p[3]])
	else:
		p[1] = Node(p[1])
		p[0] = Node("TypeDecl", [p[1],p[2]])


def p_type_spec_rep(p):
	'''TypeSpecRep : TypeSpecRep TypeSpec SEMICOLON
							   | epsilon'''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("TypeSpecRep", [p[1],p[2],p[3]])
		p[0] = Node("TypeSpecRep", [p[1],p[2]])
	else:
		p[0] = None


def p_type_spec(p):
	'''TypeSpec : AliasDecl
							| TypeDef'''
	p[0] = Node("AliasDecl", [p[1]])


def p_alias_decl(p):
	'''AliasDecl : IDENT ASSIGN Type'''
	p[1] = Node(p[1])
	p[1] = Node(p[2])
	p[0] = Node("AliasDecl", [p[1],p[2],p[3]])
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
	'''TypeDef : IDENT Type'''
	p[1] = Node(p[1])
	p[0] = Node("TypeDef", [p[1],p[2]])
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
	'''VarDecl : VAR VarSpec
					   | VAR LPAREN VarSpecRep RPAREN'''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("VarDecl", [p[1],p[2]])
	else:
		p[1] = Node(p[1])
		# p[2] = Node(p[2])
		# p[4] = Node(p[4])
		# p[0] = Node("VarDecl", [p[1],p[2],p[3],p[4]])
		p[0] = Node("VarDecl", [p[1], p[3]])


def p_var_spec_rep(p):
	'''VarSpecRep : VarSpecRep VarSpec SEMICOLON
							  | epsilon'''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("VarSpecRep", [p[1],p[2],p[3]])
		p[0] = Node("VarSpecRep", [p[1],p[2]])
	else:
		p[0] = None


def p_var_spec(p):
	'''VarSpec : IdentifierList Type ExpressionListOpt
					   | IdentifierList ASSIGN ExpressionList'''
	if p[2] == '=':
		p[2] = Node(p[2])
		p[0] = Node("VarSpec", [p[1],p[2],p[3]])
	else:
		p[0] = Node("VarSpec", [p[1],p[2],p[3]])


def p_expr_list_opt(p):
	'''ExpressionListOpt : ASSIGN ExpressionList
											 | epsilon'''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("ExpressionListOpt", [p[1],p[2]])
	else:
		p[0] = None
# -------------------------------------------------------


# ----------------SHORT VARIABLE DECLARATIONS-------------
def p_short_var_decl(p):
	''' ShortVarDecl : IDENT DEFINE Expression '''
	p[1] = Node(p[1])
	# p[2] = Node(p[2])
	p[0] = Node("ShortVarDecl" + p[2], [p[1],p[3]])
# -------------------------------------------------------


# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
	'''FunctionDecl : FUNC FunctionName Function
									| FUNC FunctionName Signature'''
	p[1] = Node(p[1])
	p[0] = Node("FunctionDecl", [p[1],p[2],p[3]])


def p_func_name(p):
	'''FunctionName : IDENT'''
	p[1] = Node(p[1])
	p[0] = Node("FunctionName", [p[1]])


def p_func(p):
	'''Function : Signature FunctionBody'''
	p[0] = Node("Function", [p[1],p[2]])


def p_func_body(p):
	'''FunctionBody : Block'''
	p[0] = Node("FunctionBody", [p[1]])
# -------------------------------------------------------


# ----------------------OPERAND----------------------------
def p_operand(p):
	'''Operand : Literal
					   | OperandName
					   | LPAREN Expression RPAREN'''
	if len(p) == 2:
		p[0] = Node("Operand", [p[1]])
	else:
		# p[1] = Node(p[1])
		# p[3] = Node(p[3])
		# p[0] = Node("Operand", [p[1], p[2], p[3]])
		p[0] = Node("Operand", [p[2]])


def p_literal(p):
	'''Literal : BasicLit'''
	# | CompositeLit'''
	p[0] = Node("Literal", [p[1]])


def p_basic_lit(p):
	'''BasicLit : INT_LITERAL
							| FLOAT_LITERAL
							| STRING_LITERAL
							| IMAG
							'''
	p[1] = Node(p[1])
	p[0] = Node("BasicLit", [p[1]])


def p_operand_name(p):
	'''OperandName : IDENT'''
	p[1] = Node(p[1])
	p[0] = Node("OperandName", [p[1]])
# ---------------------------------------------------------


# -------------------QUALIFIED IDENT----------------
def p_quali_ident(p):
	'''QualifiedIdent : IDENT PERIOD TypeName'''
	p[1] = Node(p[1])
	p[2] = Node(p[2])
	p[0] = Node("QualifiedIdent", [p[1], p[2], p[3]])
# -------------------------------------------------------


# -----------------COMPOSITE LITERALS----------------------
def p_comp_lit(p):
	'''CompositeLit : LiteralType LiteralValue'''
	p[0] = Node("CompositeLit", [p[1], p[2]])


def p_lit_type(p):
	'''LiteralType : ArrayType
							   | ElementType
							   | TypeName'''
	p[0] = Node("LiteralType", [p[1]])


def p_lit_val(p):
	'''LiteralValue : LBRACE ElementListOpt RBRACE'''
	# p[1] = Node(p[1])
	# p[3] = Node(p[3])
	# p[0] = Node("LiteralValue", [p[1], p[2], p[3]])
	p[0] = Node("LiteralValue", [p[2]])


def p_elem_list_comma_opt(p):
	'''ElementListOpt : ElementList
											   | epsilon'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("ElementListOpt", [p[1]])


def p_elem_list(p):
	'''ElementList : KeyedElement KeyedElementCommaRep'''
	p[0] = Node("ElementList", [p[1], p[2]])


def p_key_elem_comma_rep(p):
	'''KeyedElementCommaRep : KeyedElementCommaRep COMMA KeyedElement
													| epsilon'''
	if len(p) == 4:
		p[2] = Node(p[2])
		p[0] = Node("KeyedElementCommaRep", [p[1], p[2], p[3]])
	else:
		p[0] = None


def p_key_elem(p):
	'''KeyedElement : Key COLON Element
									| Element'''
	if len(p) == 4:
		p[2] = Node(p[2])
		p[0] = Node("KeyedElement", [p[1], p[2], p[3]])
	else:
		p[0] = Node("KeyedElement", [p[1]])


def p_key(p):
	'''Key : FieldName
			   | Expression
			   | LiteralValue'''
	p[0] = Node("Key", [p[1]])


def p_field_name(p):
	'''FieldName : IDENT'''
	p[1] = Node(p[1])
	p[0] = Node("FieldName", [p[1]])


def p_elem(p):
	'''Element : Expression
					   | LiteralValue'''
	p[0] = Node("Element", [p[1]])
# ---------------------------------------------------------


# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
	'''PrimaryExpr : Operand
							   | PrimaryExpr Selector
							   | Conversion
							   | PrimaryExpr Index
							   | PrimaryExpr Slice
							   | PrimaryExpr TypeAssertion
							   | PrimaryExpr Arguments'''
	if len(p) == 2:
		p[0] = Node("PrimaryExpr", [p[1]])
	else:
		p[0] = Node("PrimaryExpr", [p[1], p[2]])


def p_selector(p):
	'''Selector : PERIOD IDENT'''
	p[1] = Node(p[1])
	p[2] = Node(p[2])
	p[0] = Node("Selector", [p[1], p[2]])


def p_index(p):
	'''Index : LBRACK Expression RBRACK'''
	# p[1] = Node(p[1])
	# p[3] = Node(p[3])
	# p[0] = Node("Index", [p[1], p[2], p[3]])
	p[0] = Node("Index", [p[2]])

def p_slice(p):
	'''Slice : LBRACK ExpressionOpt COLON ExpressionOpt RBRACK
					 | LBRACK ExpressionOpt COLON Expression COLON Expression RBRACK'''
	if len(p) == 6:
		# p[1] = Node(p[1])
		p[3] = Node(p[3])
		# p[5] = Node(p[5])
		# p[0] = Node("Slice", [p[1], p[2], p[3], p[4], p[5]])
		p[0] = Node("Slice", [p[2], p[3], p[4]])
	else:
		# p[1] = Node(p[1])
		p[3] = Node(p[3])
		p[5] = Node(p[5])
		# p[7] = Node(p[7])
		# p[0] = Node("Slice", [p[1], p[2], p[3], p[4], p[5], p[6], p[7]])
		p[0] = Node("Slice", [p[2], p[3], p[4], p[5], p[6]])

def p_type_assert(p):
	'''TypeAssertion : PERIOD LPAREN Type RPAREN'''
	p[1] = Node(p[1])
	# p[2] = Node(p[2])
	# p[4] = Node(p[4])
	# p[0] = Node("TypeAssertion", [p[1], p[2], p[3], p[4]])
	p[0] = Node("TypeAssertion", [p[1], p[3]])


def p_argument(p):
	'''Arguments : LPAREN ExpressionListTypeOpt RPAREN'''
	# p[1] = Node(p[1])
	# p[3] = Node(p[3])
	# p[0] = Node("Arguments", [p[1], p[2], p[3]])
	p[0] = Node("Arguments", [p[2]])


def p_expr_list_type_opt(p):
	'''ExpressionListTypeOpt : ExpressionList
													 | epsilon'''
	if len(p) == 2:
		p[0] = Node("ExpressionListTypeOpt", [p[1]])
	else:
		p[0] = None

# def p_comma_opt(p):
#    '''CommaOpt : COMMA
#                | epsilon'''
#    if p[1] == ",":
#        p[0] = Node("", [])
#    else:
#        p[0] = Node("", [])


def p_expr_list_comma_opt(p):
	'''ExpressionListCommaOpt : COMMA ExpressionList
													  | epsilon'''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("ExpressionListCommaOpt", [p[1], p[2]])
	else:
		p[0] = None
# ---------------------------------------------------------


# ----------------------OPERATORS-------------------------
def p_expr(p):
	'''Expression : UnaryExpr
							  | Expression BinaryOp Expression'''
	if len(p) == 4:
		p[0] = Node("Expression: " + p[2], [p[1], p[3]])
	else:
		p[0] = Node("Expression", [p[1]])


def p_expr_opt(p):
	'''ExpressionOpt : Expression
									 | epsilon'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[1] = Node(p[1])
		p[0] = Node("ExpressionOpt", [p[1]])


def p_unary_expr(p):
	'''UnaryExpr : PrimaryExpr
							 | UnaryOp UnaryExpr
							 | NOT UnaryExpr'''
	if len(p) == 3 and p[1] != "!":
		p[0] = Node("UnaryExpr " + p[1], [p[2]])
	elif p[1] == "!":
		p[1] = Node(p[1])
		p[0] = Node("UnaryExpr " + p[1], [p[2]])
	else:
		p[0] = Node("UnaryExpr", [p[1]])


def p_binary_op(p):
	'''BinaryOp : LOR
							| LAND
							| RelOp
							| AddMulOp'''
	# if p[1] == "||" or p[1] == "&&":
	# 	p[1] = Node(p[1])
	# 	p[0] = Node("BinaryOp", [p[1]])
	# else:
	# 	p[0] = Node("BinaryOp", [p[1]])
	p[0] = p[1]


def p_rel_op(p):
	'''RelOp : EQL
					 | NEQ
					 | LSS
					 | GTR
					 | LEQ
					 | GEQ'''
	# p[1] = Node(p[1])
	# p[0] = Node("RelOp", [p[1]])
	p[0] = p[1]


def p_add_mul_op(p):
	'''AddMulOp : UnaryOp
							| OR
							| XOR
							| QUO
							| REM
							| SHL
							| SHR'''
	if p[1] == "/" or p[1] == "%" or p[1] == "|" or p[1] == "^" or p[1] == "<<" or p[1] == ">>":
		# p[1] = Node(p[1])
		# p[0] = Node("AddMulOp", [p[1]])
		p[0] = p[1]
	else:
		# p[0] = Node("AddMulOp", [p[1]])
		p[0] = p[1]


def p_unary_op(p):
	'''UnaryOp : ADD
					   | SUB
					   | MUL
					   | AND '''
	# if p[1] == '+' or p[1] == "-" or p[1] == "*" or p[1] == "&":
	# p[1] = Node(p[1])
	# p[0] = Node("UnaryOp", [p[1]])
	p[0] = p[1]
# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
	'''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
	p[1] = Node(p[1])
	# p[3] = Node(p[3])
	# p[5] = Node(p[5])
	p[0] = Node("Conversion", [p[1], p[2], p[4]])
# ---------------------------------------------------------


# ---------------- STATEMENTS -----------------------
def p_statement(p):
	'''Statement : Declaration
							 | LabeledStmt
							 | SimpleStmt
							 | ReturnStmt
							 | BreakStmt
							 | ContinueStmt
							 | GotoStmt
							 | Block
							 | IfStmt
							 | SwitchStmt
							 | ForStmt '''
	p[0] = Node("Statement", [p[1]])


def p_simple_stmt(p):
	''' SimpleStmt : epsilon
								   | ExpressionStmt
								   | IncDecStmt
								   | Assignment
								   | ShortVarDecl '''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("SimpleStmt", [p[1]])


def p_labeled_statements(p):
	''' LabeledStmt : Label COLON Statement '''
	p[1] = Node(p[1])
	p[2] = Node(p[2])
	p[0] = Node("LabeledStmt", [p[1], p[2], p[3]])


def p_label(p):
	''' Label : IDENT '''
	p[1] = Node(p[1])
	p[0] = Node("Label", [p[1]])


def p_expression_stmt(p):
	''' ExpressionStmt : Expression '''
	p[0] = Node("ExpressionStmt", [p[1]])


def p_inc_dec(p):
	''' IncDecStmt : Expression INC
								   | Expression DEC '''
	p[2] = Node(p[2])
	p[0] = Node("IncDecStmt", [p[1], p[2]])


def p_assignment(p):
	''' Assignment : ExpressionList assign_op ExpressionList'''
	p[0] = Node("Assignment: " + p[2], [p[1], p[3]])


def p_assign_op(p):
	''' assign_op : AssignOp'''
	# p[0] = Node("assign_op", [p[1]])
	p[0] = p[1]


def p_AssignOp(p):
	''' AssignOp : ADD_ASSIGN
							 | SUB_ASSIGN
							 | MUL_ASSIGN
							 | QUO_ASSIGN
							 | REM_ASSIGN
							 | AND_ASSIGN
							 | OR_ASSIGN
							 | XOR_ASSIGN
							 | SHL_ASSIGN
							 | SHR_ASSIGN
							 | ASSIGN '''
	p[0] = p[1]
	# p[0] = Node("AssignOp", [p[1]])


def p_if_statement(p):
	''' IfStmt : IF Expression Block ElseOpt '''
	p[1] = Node(p[1])
	p[0] = Node("IfStmt", [p[1], p[2], p[3], p[4]])


def p_SimpleStmtOpt(p):
	''' SimpleStmtOpt : SimpleStmt SEMICOLON
										  | epsilon '''
	if len(p) == 3:
		# p[2] = Node(p[2])
		# p[0] = Node("SimpleStmtOpt", [p[1], p[2]])
		p[0] = Node("SimpleStmtOpt", [p[1]])
	else:
		p[0] = None


def p_else_opt(p):
	''' ElseOpt : ELSE IfStmt
							| ELSE Block
							| epsilon '''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("ElseOpt", [p[1], p[2]])
	else:
		p[0] = None

# ----------------------------------------------------------------


# ----------- SWITCH STATEMENTS ---------------------------------

def p_switch_statement(p):
	''' SwitchStmt : ExprSwitchStmt
								   | TypeSwitchStmt '''
	p[0] = Node("SwitchStmt", [p[1]])


def p_expr_switch_stmt(p):
	''' ExprSwitchStmt : SWITCH ExpressionOpt LBRACE ExprCaseClauseRep RBRACE'''
	p[1] = Node(p[1])
	# p[3] = Node(p[3])
	# p[5] = Node(p[5])
	# p[0] = Node("ExpressionStmt", [p[1],p[2],p[3],p[4],p[5]])
	p[0] = Node("ExpressionStmt", [p[1], p[2], p[4]])


def p_expr_case_clause_rep(p):
	''' ExprCaseClauseRep : ExprCaseClauseRep ExprCaseClause
												  | epsilon'''
	if len(p) == 3:
		p[0] = Node("ExprCaseClauseRep", [p[1],p[2]])
	else:
		p[0] = None


def p_expr_case_clause(p):
	''' ExprCaseClause : ExprSwitchCase COLON StatementList'''
	p[2] = Node(p[2])
	p[0] = Node("ExprCaseClause", [p[1],p[2],p[3]])


def p_expr_switch_case(p):
	''' ExprSwitchCase : CASE ExpressionList
										   | DEFAULT '''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("ExprSwitchCase", [p[1],p[2]])
	else:
		p[1] = Node(p[1])
		p[0] = Node("ExprSwitchCase", [p[1]])


def p_type_switch_stmt(p):
	''' TypeSwitchStmt : SWITCH SimpleStmtOpt TypeSwitchGuard LBRACE TypeCaseClauseOpt RBRACE'''
	p[1] = Node(p[1])
	# p[4] = Node(p[4])
	# p[6] = Node(p[6])
	# p[0] = Node("TypeSwitchStmt", [p[1],p[2],p[3],p[4],p[5],p[6]])
	p[0] = Node("TypeSwitchStmt", [p[1], p[2], p[3], p[5]])


def p_type_switch_guard(p):
	''' TypeSwitchGuard : IdentifierOpt PrimaryExpr PERIOD LPAREN TYPE RPAREN '''

	p[3] = Node(p[3])
	# p[4] = Node(p[4])
	p[5] = Node(p[5])
	# p[6] = Node(p[6])
	# p[0] = Node("TypeSwitchGuard", [p[1],p[2],p[3],p[4],p[5],p[6]])
	p[0] = Node("TypeSwitchGuard", [p[1],p[2],p[3],p[5]])


def p_identifier_opt(p):
	''' IdentifierOpt : IDENT DEFINE
										  | epsilon '''

	if len(p) == 3:
		p[1] = Node(p[1])
		p[2] = Node(p[2])
		p[0] = Node("IdentifierOpt", [p[1],p[2]])
	else:
		p[0] = None


def p_type_case_clause_opt(p):
	''' TypeCaseClauseOpt : TypeCaseClauseOpt TypeCaseClause
												  | epsilon '''
	if len(p) == 3:
		p[0] = Node("TypeCaseClauseOpt", [p[1],p[2]])
	else:
		p[0] = None


def p_type_case_clause(p):
	''' TypeCaseClause : TypeSwitchCase COLON StatementList'''
	p[2] = Node(p[2])
	p[0] = Node("TypeCaseClause", [p[1],p[2],p[3]])


def p_type_switch_case(p):
	''' TypeSwitchCase : CASE TypeList
										   | DEFAULT '''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("TypeSwitchCase", [p[1],p[2]])
	else:
		p[1] = Node(p[1])
		p[0] = Node("", [])


def p_type_list(p):
	''' TypeList : Type TypeRep'''
	p[0] = Node("TypeList", [p[1],p[2]])


def p_type_rep(p):
	''' TypeRep : TypeRep COMMA Type
							| epsilon '''
	if len(p) == 4:
		p[2] = Node(p[2])
		p[0] = Node("TypeRep", [p[1],p[2],p[3]])
	else:
		p[0] = None

# -----------------------------------------------------------


# --------- FOR STATEMENTS AND OTHERS (MANDAL) ---------------
def p_for(p):
	'''ForStmt : FOR ConditionBlockOpt Block'''
	p[1] = Node(p[1])
	p[0] = Node("ForStmt", [p[1],p[2],p[3]])


def p_conditionblockopt(p):
	'''ConditionBlockOpt : epsilon
						   | Condition
						   | ForClause
						   | RangeClause'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("ConditionBlockOpt", [p[1]])


def p_condition(p):
	'''Condition : Expression '''
	p[0] = Node("Condition", [p[1]])


def p_forclause(p):
	'''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
	# p[2] = Node(p[2])
	# p[4] = Node(p[4])
	# p[0] = Node("ForClause", [p[1],p[2],p[3],p[4],p[5]])
	p[0] = Node("ForClause", [p[1], p[3], p[5]])

# def p_initstmtopt(p):
#   '''InitStmtOpt : epsilon
#            | InitStmt '''
#   p[0] = Node("", [])

# def p_init_stmt(p):
#   ''' InitStmt : SimpleStmt'''
#   p[0] = Node("", [])


def p_conditionopt(p):
	'''ConditionOpt : epsilon
					| Condition '''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("ConditionOpt", [p[1]])

# def p_poststmtopt(p):
#   '''PostStmtOpt : epsilon
#            | PostStmt '''
#   p[0] = Node("", [])

# def p_post_stmt(p):
#   ''' PostStmt : SimpleStmt '''
#   # p[0] = Node("", [])


def p_rageclause(p):
	'''RangeClause : ExpressionIdentListOpt RANGE Expression'''
	p[2] = Node(p[2])
	p[0] = Node("RangeClause", [p[1],p[2],p[3]])


def p_expression_ident_listopt(p):
	'''ExpressionIdentListOpt : epsilon
						   | ExpressionIdentifier'''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("ExpressionIdentListOpt", [p[1]])


def p_expressionidentifier(p):
	'''ExpressionIdentifier : ExpressionList ASSIGN'''
	p[2] = Node(p[2])
	p[0] = Node("ExpressionIdentifier", [p[1],p[2]])


def p_return(p):
	'''ReturnStmt : RETURN ExpressionListPureOpt'''
	p[1] = Node(p[1])
	p[0] = Node("ReturnStmt", [p[1],p[2]])


def p_expressionlist_pure_opt(p):
	'''ExpressionListPureOpt : ExpressionList
						   | epsilon'''
	if p[1] == "epsilon":
		p[0] = None
	p[0] = Node("ExpressionListPureOpt", [p[1]])


def p_break(p):
	'''BreakStmt : BREAK LabelOpt'''
	p[1] = Node(p[1])
	p[0] = Node("BreakStmt", [p[1],p[2]])


def p_continue(p):
	'''ContinueStmt : CONTINUE LabelOpt'''
	p[1] = Node(p[1])
	p[0] = Node("ContinueStmt", [p[1],p[2]])


def p_labelopt(p):
	'''LabelOpt : Label
				  | epsilon '''
	if p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("LabelOpt", [p[1]])


def p_goto(p):
	'''GotoStmt : GOTO Label '''
	p[1] = Node(p[1])
	p[0] = Node("GotoStmt", [p[1],p[2]])
# -----------------------------------------------------------


# ----------------  SOURCE FILE --------------------------------
def p_source_file(p):
	'''SourceFile : PackageClause SEMICOLON ImportDeclRep TopLevelDeclRep'''
	# p[2] = Node(p[2])
	p[0] = Node("SourceFile", [p[1], p[3], p[4]])


def p_import_decl_rep(p):
	'''ImportDeclRep : epsilon
					 | ImportDeclRep ImportDecl SEMICOLON'''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("ImportDeclRep",[p[1],p[2],p[3]])
		p[0] = Node("ImportDeclRep",[p[1], p[2]])
	else:
		p[0] = None


def p_toplevel_decl_rep(p):
	'''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl SEMICOLON
										   | epsilon'''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("TopLevelDeclRep", [p[1], p[2], p[3]])
		p[0] = Node("TopLevelDeclRep", [p[1], p[2]])
	else:
		p[0] = None
# --------------------------------------------------------


# ---------- PACKAGE CLAUSE --------------------
def p_package_clause(p):
	'''PackageClause : PACKAGE PackageName'''
	p[1] = Node(p[1])
	p[0] = Node("PackageClause", [p[1], p[2]])


def p_package_name(p):
	'''PackageName : IDENT'''
	p[1] = Node(p[1])
	p[0] = Node("PackageName", [p[1]])
# -----------------------------------------------


# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
	'''ImportDecl : IMPORT ImportSpec
					| IMPORT LPAREN ImportSpecRep RPAREN '''
	if len(p) == 3:
		p[1] = Node(p[1])
		p[0] = Node("ImportDecl", [p[1], p[2]])
	else:
		p[1] = Node(p[1])
		# p[2] = Node(p[2])
		# p[4] = Node(p[4])
		# p[0] = Node("ImportDecl", [p[1], p[2], p[3], p[4]])
		p[0] = Node("ImportDecl", [p[1], p[3]])


def p_import_spec_rep(p):
	''' ImportSpecRep : ImportSpecRep ImportSpec SEMICOLON
						  | epsilon '''
	if len(p) == 4:
		# p[3] = Node(p[3])
		# p[0] = Node("ImportSpecRep", [p[1], p[2], p[3]])
		mylist2 = []
		if p[1] != None:
			mylist2.extend(p[1].children)
		mylist2.append(p[2])
		p[0] = Node("StatementRep",mylist2)
	else:
		p[0] = None


def p_import_spec(p):
	''' ImportSpec : PackageNameDotOpt ImportPath '''
	p[0] = Node("ImportSpec", [p[1], p[2]])


def p_package_name_dot_opt(p):
	''' PackageNameDotOpt : PERIOD
												  | PackageName
												  | epsilon'''
	if p[1] == '.':
		p[1] = Node(p[1])
		p[0] = Node("PackageNameDotOpt", [p[1]])
	elif p[1] == "epsilon":
		p[0] = None
	else:
		p[0] = Node("PackageNameDotOpt", [p[1]])


def p_import_path(p):
	''' ImportPath : STRING_LITERAL '''
	p[1] = Node(p[1])
	p[0] = Node("ImportPath", [p[1]])
# -------------------------------------------------------


def p_empty(p):
	'''epsilon : '''
	p[0] = "epsilon"

# def p_import_decl(p):


# def p_start(p):
#   '''start : expression'''
#   # p[0] = "<start>" + p[1] + "</start>"
#   p[0] = Node("", [])

# def p_expression_plus(p):
#     '''expression : expression ADD term
#                   | expression SUB term'''
#     if p[2] == '+':
#         # p[0] = "<expr>" + p[1] + "</expr> + " + p[3]
#         p[0] = Node("", [])
#     else:
#         # p[0] = "<expr>" + p[1] + "</expr> - " + p[3]
#         p[0] = Node("", [])
#         # p[0] = p[1] - p[3]
# # def p_expression_minus(p):
# #     'expression : '

# def p_expression_term(p):
#     'expression : term'
#     # p[0] = "<term>" + p[1] + "</term>"
#     p[0] = Node("", [])

# def p_term_times(p):
#     'term : term MUL factor'
#     # p[0] = "<term>" + p[1] + "</term> * " + "<factor>" + p[3] + "</factor>"
#     p[0] = Node("", [])


# # def p_term_div(p):
# #     'term : term QUO factor'
# #     p[0] = p[1] / p[3]

# def p_term_factor(p):
#     'term : factor'
#     p[0] = Node("", [])

# def p_factor_num(p):
#     'factor : INTEGER'
#     # p[0] = str([p[1]])
#     p[0] = Node("", [])

# # def p_factor_expr(p):
# #     'factor : LPAREN expression RPAREN'
# #     p[0] = p[2]


# Error rule for syntax errors


def p_error(p):
	print("Error in parsing!")
	print("Error at: ", p.type)
	sys.exit()


parser = argparse.ArgumentParser(description='Scans and Parses the input .go file and builds the corresponding AST')

# parser.add_argument('--cfg', dest='config_file_location', help='Location of the input .go file', required=True)

parser.add_argument('--output', dest='out_file_location', help='Location of the output .html file', required=True)

parser.add_argument('--input', dest='in_file_location', help='Location of the output .html file', required=True)

result = parser.parse_args()
# config_file_location = str(result.config_file_location)
out_file_location = str(result.out_file_location)
in_file_location = str(result.in_file_location)


# Build lexer
lexer = lex.lex()
# lexer.abcde = 0   # custom global varibales for lexer

# Read input file
in_file = open(in_file_location,'r')

# Open output file
out_file = open(out_file_location,"w+")
out_file.write('strict digraph G {\n')

data = in_file.read()

# Iterate to get tokens
parser = yacc.yacc()
res = parser.parse(data)

out_file.write("}\n")
# Close file
out_file.close()
in_file.close()


# # Read input file
# in_file_location = "input.go"
# in_file = open(in_file_location, 'r')
# out_file = open("output.dot", "w")
# out_file.write('strict digraph G {\n')
#
# data = in_file.read()
# 
# # Iterate to get tokens
# parser = yacc.yacc()
# res = parser.parse(data)
#
# out_file.write("}\n")
# # Close file
# out_file.close()
# in_file.close()
