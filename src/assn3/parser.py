from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc
from lexer import *
from data_structures import Helper, Node
import json
import argparse
import sys

"""
CITE:
  Most of the token definations are taken from documentation
  of golang(go docs), and some from the token (go/token)
  package of golang: https://golang.org/src/go/token/token.go
"""

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

# declarations
helper = Helper()
rootNode = None
helper.newScope()
# ------------------------START----------------------------


def p_start(p):
	'''start : SourceFile'''
	p[0] = p[1]
	p[0].name = 'start'
	global rootNode
	rootNode = p[0]

# -------------------------------------------------------


# -----------------------TYPES---------------------------
def p_type(p):
	'''Type : TypeName
					| TypeLit
					| LPAREN Type RPAREN'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = p[2]
	p[0].name = 'Type'


def p_type_name(p):
	'''TypeName : TypeToken
							| QualifiedIdent'''
	p[0] = p[1]
	p[0].name = 'TypeName'

def p_type_token(p):
	'''TypeToken : INT
							 | FLOAT
							 | STRING
							 | BOOL
							 | COMPLEX
							 | TYPE IDENT'''

	p[0] = Node('TypeToken')
	if len(p) == 2:
		p[0].typeList.append(p[1])
	else:
		if not helper.checkId(p[2],'default'):
			compilation_errors.add('TypeError', line_number.get()+1,\
						   'Type %s not defined'%p[2])
		else:
			info = helper.findInfo(p[2],'default')
			if info == None:
				compilation_errors.add('NameError', line_number.get()+1,\
						   'Identifier %s not defined'%p[2])
			p[0].typeList.append(info['type'])



def p_type_lit(p):
	'''TypeLit : ArrayType
					   | StructType
					   | PointerType'''
	p[0] = p[1]
	p[0].name = 'TypeLit'

def p_type_opt(p):
	'''TypeOpt : Type
					   | epsilon'''
	p[0] = p[1]
	p[0].name = 'TypeOpt'

# -------------------------------------------------------


# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
	'''ArrayType : LBRACK ArrayLength RBRACK ElementType'''
	# TODO
	p[0] = Node('ArrayType')
	p[0].code = p[2].code
	p[0].typeList.append()
	p[0].name = 'ArrayType'

def p_array_length(p):
	''' ArrayLength : Expression '''
	p[0] = p[1]
	p[0].name = 'ArrayLength'

def p_element_type(p):
	''' ElementType : Type '''
	p[0] = p[1]
	p[0].name = 'ElementType'

# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
	'''StructType : STRUCT LBRACE FieldDeclRep RBRACE'''
	# TODO
	p[0] = p[4]
	info = helper.findInfo(p[2],'default')
	p[0].name = 'StructType'

def p_field_decl_rep(p):
	''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
									| epsilon '''
    p[0] = p[1]
    p[0].name = 'FieldDeclRep'
    if len(p) == 4:
        p[0].idList += p[2].idList
        p[0].typeList += p[2].typeList


def p_field_decl(p):
	''' FieldDecl : IdentifierList Type'''
    p[0] = p[1]
    p[0].namr = 'FieldDecl'

    for i in p[0].idList:
        helper.symbolTables[helper.getScope()].update(i, 'type', p[2].typeList[0])


# NOT REQUIRED

def p_TagOpt(p):
	''' TagOpt : Tag
				| epsilon '''
# Not used


def p_Tag(p):
	''' Tag : STRING_LITERAL '''
# Not used

# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
	'''PointerType : MUL BaseType'''
    p[0] = p[2]
    p[0].name = 'PointerType'
    p[0].typeList[0].insert('*', 0)


def p_base_type(p):
	'''BaseType : Type'''
    p[0] = p[1]
    p[0].name = 'BaseType'

# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
	'''Signature : Parameters ResultOpt'''



def p_result_opt(p):
	'''ResultOpt : Result
							 | epsilon'''



def p_result(p):
	'''Result : Parameters
					  | Type'''



def p_params(p):
	'''Parameters : LPAREN ParameterListOpt RPAREN'''




def p_param_list_opt(p):
	'''ParameterListOpt : ParametersList
													 | epsilon'''



def p_param_list(p):
	'''ParametersList : Type
									  | IdentifierList Type
									  | ParameterDeclCommaRep'''



def p_param_decl_comma_rep(p):
	'''ParameterDeclCommaRep : ParameterDeclCommaRep COMMA ParameterDecl
													 | ParameterDecl COMMA ParameterDecl'''



def p_param_decl(p):
	'''ParameterDecl : IdentifierList Type
									 | Type'''

# ---------------------------------------------------------


# -----------------------BLOCKS---------------------------
def p_block(p):
	'''Block : LBRACE StatementList RBRACE'''
	p[0] = p[2]
	p[0].name = 'Block'


def p_stat_list(p):
	'''StatementList : StatementRep'''
	p[0] = p[1]
	p[0].name = 'StatementList'


def p_stat_rep(p):
	'''StatementRep : StatementRep Statement SEMICOLON
									| epsilon'''
	p[0] = p[1]
	p[0].name = 'StatementRep'
	if len(p) == 4:
		p[0].code += p[2].code

# -------------------------------------------------------


# ------------------DECLARATIONS and SCOPE------------------------
def p_decl(p):
	'''Declaration : ConstDecl
								   | TypeDecl
								   | VarDecl'''
	p[0] = p[1]
	p[0].name = 'Declaration'

def p_toplevel_decl(p):
	'''TopLevelDecl : Declaration
									| FunctionDecl'''
	p[0] = p[1]
	p[0].name = 'TopLevelDecl'
# -------------------------------------------------------


# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
	'''ConstDecl : CONST ConstSpec
							 | CONST LPAREN ConstSpecRep RPAREN'''
	if len(p) == 3:
		p[0] = p[2]
	else:
		p[0] = p[3]
	p[0].name = 'ConstDecl'


def p_const_spec_rep(p):
	'''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
									| epsilon'''
	p[0] = p[1]
	p[0].name = 'ConstSpecRep'
	if len(p) == 4:
		p[0].code += p[2].code


def p_const_spec(p):
	'''ConstSpec : IdentifierList Type ASSIGN ExpressionList'''
	p[0] = Node('ConstSpec')
	p[0].code = p[1].code + p[4].code
	if len(p[1].placeList) != len(p[4].placeList):
		compilation_errors.add('AssignmentError', line_number.get()+1,\
			"Number of expressions does not match number of identifiers")
	else:
		for idx in range(len(p[1].placeList)):
			# if condition not used
			p[0].code.append(["=", p[1].placelist[idx], p[4].placelist[idx]])
			p[1].placelist[idx] = p[4].placelist[idx]

			scope = helper.findScope(p[1].identList[idx])

			helper.symbolTables[scope].update(p[1].identList[idx], 'place', p[1].placeList[idx])
			helper.symbolTables[scope].update(p[1].identList[idx], 'type', p[2].typeList[idx])

			# TODO typechecking

def p_identifier_list(p):
	'''IdentifierList : IDENT IdentifierRep'''
	p[0] = p[2]
	p[0].name = 'IdentifierList'
	p[0].identList.insert(0,p[1])

	if helper.checkId(p[1],'current'):
		compilation_errors.add("Redeclare Error", line_number.get()+1,\
			"%s already declared"%p[1])
	else:
		helper.symbolTables[helper.getScope()].add(p[1],None)
		newTemp = helper.newVar()
		p[0].placeList.insert(0,newTemp)
		helper.symbolTables[helper.getScope()].update(p[1],'place',newTemp)


def p_identifier_rep(p):
	'''IdentifierRep : IdentifierRep COMMA IDENT
									 | epsilon'''

	p[0] = p[1]
	p[0].name = 'IdentifierRep'
	if len(p) == 4:
		if helper.checkId(p[3], 'current'):
			compilation_errors.add("Redeclare Error", line_number.get()+1,\
			"%s already declared"%p[1])
		else:
			helper.symbolTables[helper.getScope()].add(p[3],None)
			newTemp = helper.newVar()
			p[0].placelist.append(newTemp)
			helper.symbolTables[helper.getScope()].update(p[3],'place',newTemp)
			p[0].idList.append(p[3])


def p_expr_list(p):
	'''ExpressionList : Expression ExpressionRep'''
	p[0] = p[1]
	p[0].name = 'ExpressionList'
	p[0].code += p[2].code
	p[0].placeList += p[2].placeList
	p[0].identList += p[2].identList
	# TODO understand addrlist


def p_expr_rep(p):
	'''ExpressionRep : ExpressionRep COMMA Expression
									 | epsilon'''

	p[0] = p[1]
	p[0].name = 'ExpressionRep'
	if len(p) == 4:
		p[0].code += p[3].code
		p[0].placeList += p[3].placeList
		p[0].identList += p[3].identList
	# TODO understand addrlist

# -------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
	'''TypeDecl : TYPE TypeSpec
							| TYPE LPAREN TypeSpecRep RPAREN'''
	if len(p) == 5:
		p[0] = p[3]
	else:
		p[0] = p[2]
	p[0].name = 'TypeDecl'


def p_type_spec_rep(p):
	'''TypeSpecRep : TypeSpecRep TypeSpec SEMICOLON
							   | epsilon'''
	if len(p) == 4:
		p[0] = Node('TypeSpecRep')
		# TODO ommitting RHS why?
	else:
		p[0] = p[1]


def p_type_spec(p):
	'''TypeSpec : AliasDecl
							| TypeDef'''
	p[0] = p[1]
	p[0].name = 'TypeSpec'


def p_alias_decl(p):
	'''AliasDecl : IDENT ASSIGN Type'''
	# Not used
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
	'''TypeDef : IDENT Type'''
    p[0] = Node('Typedef')

	if helper.checkId(p[1],'current'):
		compilation_errors.add("Redeclare Error", line_number.get()+1,\
			"%s already declared"%p[1])
	else:
		helper.symbolTables[helper.getScope()].add(p[1], p[2].TypeList[0])
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
	'''VarDecl : VAR VarSpec
					   | VAR LPAREN VarSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[3]
    p[0].name = 'VarDecl'

def p_var_spec_rep(p):
	'''VarSpecRep : VarSpecRep VarSpec SEMICOLON
							  | epsilon'''
    p[0] = p[1]
    p[0].name = 'VarSpecRep'
    if len(p) == 4:
        p[0].code += p[2].code


def p_var_spec(p):
	'''VarSpec : IdentifierList Type ExpressionListOpt
					   | IdentifierList ASSIGN ExpressionList'''
    # TODO


def p_expr_list_opt(p):
	'''ExpressionListOpt : ASSIGN ExpressionList
											 | epsilon'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[1]
    p[0].name = 'ExpressionListOpt'

# -------------------------------------------------------




# ----------------SHORT VARIABLE DECLARATIONS-------------
def p_short_var_decl(p):
	''' ShortVarDecl : IDENT DEFINE Expression '''
    p[0] = Node('IdentifierList')

	if helper.checkId(p[1],'current'):
		compilation_errors.add("Redeclare Error", line_number.get()+1,\
			"%s already declared"%p[1])
	else:
		helper.symbolTables[helper.getScope()].add(p[1],None)
		newTemp = helper.newVar()
        p[0].code - p[3].code
        p[0].code.append(['=', newTemp, p[3].placelist[0]])
        helper.symbolTables[helper.getScope()].update(p[1],'place',newTemp)
        helper.symbolTables[helper.getScope()].update(p[1], 'type', p[3].typeList[0])
# -------------------------------------------------------




# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
	'''FunctionDecl : FUNC FunctionName Function
									| FUNC FunctionName Signature'''


def p_func_name(p):
	'''FunctionName : IDENT'''


def p_func(p):
	'''Function : Signature FunctionBody'''


def p_func_body(p):
	'''FunctionBody : Block'''
# -------------------------------------------------------


# ----------------------OPERAND----------------------------
def p_operand(p):
	'''Operand : Literal
					   | OperandName
					   | LPAREN Expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
    p[0].name = 'Operand'

def p_literal(p):
	'''Literal : BasicLit'''
    p[0] = p[1]
    p[0].name = 'Literal'

def p_basic_lit(p):
	'''BasicLit : INT_LITERAL
							| FLOAT_LITERAL
							| STRING_LITERAL
							| IMAG
							'''


def p_operand_name(p):
	'''OperandName : IDENT'''

# ---------------------------------------------------------


# -------------------QUALIFIED IDENT----------------
def p_quali_ident(p):
	'''QualifiedIdent : IDENT PERIOD TypeName'''

# -------------------------------------------------------


# -----------------COMPOSITE LITERALS----------------------
def p_comp_lit(p):
	'''CompositeLit : LiteralType LiteralValue'''



def p_lit_type(p):
	'''LiteralType : ArrayType
							   | ElementType
							   | TypeName'''



def p_lit_val(p):
	'''LiteralValue : LBRACE ElementListOpt RBRACE'''



def p_elem_list_comma_opt(p):
	'''ElementListOpt : ElementList
											   | epsilon'''



def p_elem_list(p):
	'''ElementList : KeyedElement KeyedElementCommaRep'''


def p_key_elem_comma_rep(p):
	'''KeyedElementCommaRep : KeyedElementCommaRep COMMA KeyedElement
													| epsilon'''


def p_key_elem(p):
	'''KeyedElement : Key COLON Element
									| Element'''



def p_key(p):
	'''Key : FieldName
			   | Expression
			   | LiteralValue'''



def p_field_name(p):
	'''FieldName : IDENT'''



def p_elem(p):
	'''Element : Expression
					   | LiteralValue'''

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



def p_selector(p):
	'''Selector : PERIOD IDENT'''



def p_index(p):
	'''Index : LBRACK Expression RBRACK'''


def p_slice(p):
	'''Slice : LBRACK ExpressionOpt COLON ExpressionOpt RBRACK
					 | LBRACK ExpressionOpt COLON Expression COLON Expression RBRACK'''


def p_type_assert(p):
	'''TypeAssertion : PERIOD LPAREN Type RPAREN'''



def p_argument(p):
	'''Arguments : LPAREN ExpressionListTypeOpt RPAREN'''



def p_expr_list_type_opt(p):
	'''ExpressionListTypeOpt : ExpressionList
													 | epsilon'''



def p_expr_list_comma_opt(p):
	'''ExpressionListCommaOpt : COMMA ExpressionList
													  | epsilon'''

# ---------------------------------------------------------


# ----------------------OPERATORS-------------------------
def p_expr(p):
	'''Expression : UnaryExpr
							  | Expression BinaryOp Expression'''



def p_expr_opt(p):
	'''ExpressionOpt : Expression
									 | epsilon'''


def p_unary_expr(p):
	'''UnaryExpr : PrimaryExpr
							 | UnaryOp UnaryExpr
							 | NOT UnaryExpr'''



def p_binary_op(p):
	'''BinaryOp : LOR
							| LAND
							| RelOp
							| AddMulOp'''



def p_rel_op(p):
	'''RelOp : EQL
					 | NEQ
					 | LSS
					 | GTR
					 | LEQ
					 | GEQ'''



def p_add_mul_op(p):
	'''AddMulOp : UnaryOp
							| OR
							| XOR
							| QUO
							| REM
							| SHL
							| SHR'''



def p_unary_op(p):
	'''UnaryOp : ADD
					   | SUB
					   | MUL
					   | AND '''

# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
	'''Conversion : TYPECAST Type LPAREN Expression RPAREN'''

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



def p_simple_stmt(p):
	''' SimpleStmt : epsilon
								   | ExpressionStmt
								   | IncDecStmt
								   | Assignment
								   | ShortVarDecl '''



def p_labeled_statements(p):
	''' LabeledStmt : Label COLON Statement '''



def p_label(p):
	''' Label : IDENT '''



def p_expression_stmt(p):
	''' ExpressionStmt : Expression '''



def p_inc_dec(p):
	''' IncDecStmt : Expression INC
								   | Expression DEC '''



def p_assignment(p):
	''' Assignment : ExpressionList assign_op ExpressionList'''



def p_assign_op(p):
	''' assign_op : AssignOp'''



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



def p_if_statement(p):
	''' IfStmt : IF Expression Block ElseOpt '''



def p_SimpleStmtOpt(p):
	''' SimpleStmtOpt : SimpleStmt SEMICOLON
										  | epsilon '''



def p_else_opt(p):
	''' ElseOpt : ELSE IfStmt
							| ELSE Block
							| epsilon '''


# ----------------------------------------------------------------


# ----------- SWITCH STATEMENTS ---------------------------------

def p_switch_statement(p):
	''' SwitchStmt : ExprSwitchStmt
								   | TypeSwitchStmt '''



def p_expr_switch_stmt(p):
	''' ExprSwitchStmt : SWITCH ExpressionOpt LBRACE ExprCaseClauseRep RBRACE'''



def p_expr_case_clause_rep(p):
	''' ExprCaseClauseRep : ExprCaseClauseRep ExprCaseClause
												  | epsilon'''



def p_expr_case_clause(p):
	''' ExprCaseClause : ExprSwitchCase COLON StatementList'''



def p_expr_switch_case(p):
	''' ExprSwitchCase : CASE ExpressionList
										   | DEFAULT '''



def p_type_switch_stmt(p):
	''' TypeSwitchStmt : SWITCH SimpleStmtOpt TypeSwitchGuard LBRACE TypeCaseClauseOpt RBRACE'''



def p_type_switch_guard(p):
	''' TypeSwitchGuard : IdentifierOpt PrimaryExpr PERIOD LPAREN TYPE RPAREN '''



def p_identifier_opt(p):
	''' IdentifierOpt : IDENT DEFINE
										  | epsilon '''



def p_type_case_clause_opt(p):
	''' TypeCaseClauseOpt : TypeCaseClauseOpt TypeCaseClause
												  | epsilon '''



def p_type_case_clause(p):
	''' TypeCaseClause : TypeSwitchCase COLON StatementList'''



def p_type_switch_case(p):
	''' TypeSwitchCase : CASE TypeList
										   | DEFAULT '''



def p_type_list(p):
	''' TypeList : Type TypeRep'''


def p_type_rep(p):
	''' TypeRep : TypeRep COMMA Type
							| epsilon '''


# -----------------------------------------------------------


# --------- FOR STATEMENTS AND OTHERS (MANDAL) ---------------
def p_for(p):
	'''ForStmt : FOR ConditionBlockOpt Block'''



def p_conditionblockopt(p):
	'''ConditionBlockOpt : epsilon
						   | Condition
						   | ForClause
						   | RangeClause'''



def p_condition(p):
	'''Condition : Expression '''



def p_forclause(p):
	'''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''



def p_conditionopt(p):
	'''ConditionOpt : epsilon
					| Condition '''



def p_rageclause(p):
	'''RangeClause : ExpressionIdentListOpt RANGE Expression'''



def p_expression_ident_listopt(p):
	'''ExpressionIdentListOpt : epsilon
						   | ExpressionIdentifier'''



def p_expressionidentifier(p):
	'''ExpressionIdentifier : ExpressionList ASSIGN'''



def p_return(p):
	'''ReturnStmt : RETURN ExpressionListPureOpt'''



def p_expressionlist_pure_opt(p):
	'''ExpressionListPureOpt : ExpressionList
						   | epsilon'''



def p_break(p):
	'''BreakStmt : BREAK LabelOpt'''



def p_continue(p):
	'''ContinueStmt : CONTINUE LabelOpt'''



def p_labelopt(p):
	'''LabelOpt : Label
				  | epsilon '''



def p_goto(p):
	'''GotoStmt : GOTO Label '''

# -----------------------------------------------------------


# ----------------  SOURCE FILE --------------------------------
def p_source_file(p):
	'''SourceFile : PackageClause SEMICOLON ImportDeclRep TopLevelDeclRep'''
	p[0] = p[4]
	p[0].name = 'SourceFile'

def p_import_decl_rep(p):
	'''ImportDeclRep : epsilon
					 | ImportDeclRep ImportDecl SEMICOLON'''
	p[0] = Node('ImportDeclRep')


def p_toplevel_decl_rep(p):
	'''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl SEMICOLON
										   | epsilon'''
	p[0] = Node('TopLevelDeclRep')
	if len(p) != 2:
		p[0].code = p[1].code + p[2].code


# --------------------------------------------------------


# ---------- PACKAGE CLAUSE --------------------
def p_package_clause(p):
	'''PackageClause : PACKAGE PackageName'''
	p[0] = p[1]
	p[0].name = 'PackageClause'



def p_package_name(p):
	'''PackageName : IDENT'''
	p[0] = Node('PackageName')
	p[0].identlist.append(p[1])
	helper.symbolTables[helper.getScope()].updateMetadata('package', p[1])

# -----------------------------------------------


# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
	'''ImportDecl : IMPORT ImportSpec
					| IMPORT LPAREN ImportSpecRep RPAREN '''
	p[0] = Node('ImportDecl')

def p_import_spec_rep(p):
	''' ImportSpecRep : ImportSpecRep ImportSpec SEMICOLON
						  | epsilon '''
	p[0] = Node('ImportSpecRep')


def p_import_spec(p):
	''' ImportSpec : PackageNameDotOpt ImportPath '''
	p[0] = Node('ImportSpec')

def p_package_name_dot_opt(p):
	''' PackageNameDotOpt : PERIOD
												  | PackageName
												  | epsilon'''
	p[0] = Node('PackageNameDotOpt')


def p_import_path(p):
	''' ImportPath : STRING_LITERAL '''
	p[0] = Node('ImportPath')
# -------------------------------------------------------


def p_empty(p):
	'''epsilon : '''
	p[0] = Node('epsilon')


# Error rule for syntax errors


def p_error(p):
	# plus one as line number starts from 0
	compilation_errors.add('Parsing Error', line_number.get()+1,\
						   'Error occured at the token: %s'%p.type)


parser = argparse.ArgumentParser(description='Scans and Parses the input .go file and builds the corresponding AST')

# parser.add_argument('--cfg', dest='config_file_location', help='Location of the input .go file', required=True)

parser.add_argument('--output', dest='out_file_location', help='Location of the output .dot file', required=True)

parser.add_argument('--input', dest='in_file_location', help='Location of the input .go file', required=True)

result = parser.parse_args()
# config_file_location = str(result.config_file_location)
out_file_location = str(result.out_file_location)
in_file_location = str(result.in_file_location)


# Build lexer
lexer = lex.lex()

# Read input file
in_file = open(in_file_location,'r')

# Open output file
out_file = open(out_file_location,"w+")
out_file.write('strict digraph G {\n')

data = in_file.read()

# Iterate to get tokens
parser = yacc.yacc()
res = parser.parse(data)

if compilation_errors.size() > 0:
	compilation_errors.printErrors()
	sys.exit(0)

out_file.write("}\n")
# Close file
out_file.close()
in_file.close()
