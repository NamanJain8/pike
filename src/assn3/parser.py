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



def p_type_name(p):
	'''TypeName : TypeToken
							| QualifiedIdent'''



def p_type_token(p):
	'''TypeToken : INT
							 | FLOAT
							 | STRING
							 | BOOL
							 | COMPLEX
							 | TYPE IDENT'''



def p_type_lit(p):
	'''TypeLit : ArrayType
					   | StructType
					   | PointerType'''



def p_type_opt(p):
	'''TypeOpt : Type
					   | epsilon'''

# -------------------------------------------------------


# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
	'''ArrayType : LBRACK ArrayLength RBRACK ElementType'''




def p_array_length(p):
	''' ArrayLength : Expression '''



def p_element_type(p):
	''' ElementType : Type '''


# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
	'''StructType : STRUCT LBRACE FieldDeclRep RBRACE'''



def p_field_decl_rep(p):
	''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
									| epsilon '''



def p_field_decl(p):
	''' FieldDecl : IdentifierList Type TagOpt'''



def p_TagOpt(p):
	''' TagOpt : Tag
				| epsilon '''



def p_Tag(p):
	''' Tag : STRING_LITERAL '''

# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
	'''PointerType : MUL BaseType'''



def p_base_type(p):
	'''BaseType : Type'''

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



def p_stat_list(p):
	'''StatementList : StatementRep'''



def p_stat_rep(p):
	'''StatementRep : StatementRep Statement SEMICOLON
									| epsilon'''

# -------------------------------------------------------


# ------------------DECLARATIONS and SCOPE------------------------
def p_decl(p):
	'''Declaration : ConstDecl
								   | TypeDecl
								   | VarDecl'''



def p_toplevel_decl(p):
	'''TopLevelDecl : Declaration
									| FunctionDecl'''

# -------------------------------------------------------


# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
	'''ConstDecl : CONST ConstSpec
							 | CONST LPAREN ConstSpecRep RPAREN'''



def p_const_spec_rep(p):
	'''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
									| epsilon'''



def p_const_spec(p):
	'''ConstSpec : IdentifierList TypeExprListOpt'''



def p_type_expr_list(p):
	'''TypeExprListOpt : TypeOpt ASSIGN ExpressionList
									   | epsilon'''



def p_identifier_list(p):
	'''IdentifierList : IDENT IdentifierRep'''



def p_identifier_rep(p):
	'''IdentifierRep : IdentifierRep COMMA IDENT
									 | epsilon'''



def p_expr_list(p):
	'''ExpressionList : Expression ExpressionRep'''



def p_expr_rep(p):
	'''ExpressionRep : ExpressionRep COMMA Expression
									 | epsilon'''

# -------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
	'''TypeDecl : TYPE TypeSpec
							| TYPE LPAREN TypeSpecRep RPAREN'''



def p_type_spec_rep(p):
	'''TypeSpecRep : TypeSpecRep TypeSpec SEMICOLON
							   | epsilon'''



def p_type_spec(p):
	'''TypeSpec : AliasDecl
							| TypeDef'''



def p_alias_decl(p):
	'''AliasDecl : IDENT ASSIGN Type'''

# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
	'''TypeDef : IDENT Type'''

# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
	'''VarDecl : VAR VarSpec
					   | VAR LPAREN VarSpecRep RPAREN'''



def p_var_spec_rep(p):
	'''VarSpecRep : VarSpecRep VarSpec SEMICOLON
							  | epsilon'''



def p_var_spec(p):
	'''VarSpec : IdentifierList Type ExpressionListOpt
					   | IdentifierList ASSIGN ExpressionList'''



def p_expr_list_opt(p):
	'''ExpressionListOpt : ASSIGN ExpressionList
											 | epsilon'''

# -------------------------------------------------------




# ----------------SHORT VARIABLE DECLARATIONS-------------
def p_short_var_decl(p):
	''' ShortVarDecl : IDENT DEFINE Expression '''
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


def p_literal(p):
	'''Literal : BasicLit'''



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