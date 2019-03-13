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

size_mp = {}
size_mp['float']   = 4
size_mp['int']     = 4
size_mp['bool']    = 1
size_mp['complex'] = 8
size_mp['string']  = 4

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
    '''Type : TypeToken
                    | TypeLit
                    | LPAREN Type RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
    p[0].name = 'Type'


def p_type_token(p):
    '''TypeToken : INT
                             | FLOAT
                             | STRING
                             | BOOL
                             | TYPE IDENT'''
    p[0] = Node('TypeToken')
    if len(p) == 2:
        p[0].typeList.append(p[1])
        p[0].sizeList.append(size_mp[p[1]])
    else:
        tmpMap = helper.symbolTables[helper.getScope()].typeDefs[p[2]]
        if tmpMap is None:
            compilation_errors.add('Type Error', line_number.get()+1, 'undefined: '+p[2])
        else:
            p[0].sizeList.append(tmpMap['size'])
            p[0].typeList.append(p[2])

def p_type_lit(p):
    '''TypeLit : ArrayType
                       | StructType
                       | PointerType'''
    p[0] = p[1]
    p[0].name = 'TypeLit'

# -------------------------------------------------------


# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
    '''ArrayType : LBRACK ArrayLength RBRACK ElementType'''
    # TODO
    p[0] = Node('ArrayType')
    p[0].code = p[2].code
    p[0].typeList.append(['array',p[2].extra['count'],p[4].typeList[0]])
    p[0].sizeList.append(int(p[2].extra['count']*p[4].sizeList[0]))
    p[0].name = 'ArrayType'

def p_array_length(p):
    ''' ArrayLength : INT_LITERAL'''
    p[0] = Node('ArrayLength')
    p[0].extra['count'] = int(p[1])

def p_element_type(p):
    ''' ElementType : Type '''
    p[0] = p[1]
    p[0].name = 'ElementType'

# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
    '''StructType : STRUCT LBRACE FieldDeclRep RBRACE'''
    # TODO create scope
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
    p[0] = Node('FieldDecl')

    for identifier in p[1].identList:
        helper.symbolTables[helper.getScope()].update(identifier, 'type', p[2].typeList[0])
        helper.symbolTables[helper.getScope()].update(identifier, 'size', p[2].sizeList[0])


# NOT REQUIRED

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
    # if len(p) == 4:
    #     p[0].code += p[2].code

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
    p[0].code = p[4].code
    if len(p[1].placeList) != len(p[4].placeList):
        compilation_errors.add('AssignmentError', line_number.get()+1,\
            "Number of expressions does not match number of identifiers")
    else:
        for idx in range(len(p[1].placeList)):
            # if condition not used
            if helper.checkId(p[1].identList[idx],'current'):
                compilation_errors.add("Redeclare Error", line_number.get()+1,\
                    "Constant %s already declared"%p[1].identList[idx])
            else:
                p[0].code.append(["=", p[1].placelist[idx], p[4].placelist[idx]])
                p[1].placelist[idx] = p[4].placelist[idx]

                # scope = helper.findScope(p[1].identList[idx])
                helper.symbolTables[helper.getScope()].add(p[1].identList[idx],p[1].typeList[idx])

                helper.symbolTables[helper.getScope()].update(p[1].identList[idx], 'place', p[1].placeList[idx])
                helper.symbolTables[helper.getScope()].update(p[1].identList[idx], 'type', p[2].typeList[idx])

                # TODO typechecking

def p_identifier_list(p):
    '''IdentifierList : IDENT IdentifierRep'''
    p[0] = p[2]
    p[0].name = 'IdentifierList'

    if helper.checkId(p[1],'current') or (p[1] in p[2].identList):
        compilation_errors.add("Redeclare Error", line_number.get()+1,\
            "%s already declared"%p[1])
    else:
        p[0].identList.insert(0,p[1])


def p_identifier_rep(p):
    '''IdentifierRep : IdentifierRep COMMA IDENT
                                     | epsilon'''
    p[0] = p[1]
    p[0].name = 'IdentifierRep'
    if len(p) == 4:
        if helper.checkId(p[3], 'current') or (p[3] in p[0].identList):
            compilation_errors.add("Redeclare Error", line_number.get()+1,\
            "%s already declared"%p[1])
        else:
            p[0].identList.append(p[3])


def p_expr_list(p):
    '''ExpressionList : Expression ExpressionRep'''
    p[0] = p[1]
    p[0].name = 'ExpressionList'
    # p[0].code += p[2].code
    p[0].placeList += p[2].placeList
    p[0].typeList += p[2].typeList
    # TODO understand addrlist


def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                                     | epsilon'''

    p[0] = p[1]
    p[0].name = 'ExpressionRep'
    if len(p) == 4:
        p[0].code += p[3].code
        p[0].placeList += p[3].placeList
        p[0].typeList += p[3].typeList
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
        helper.symbolTables[helper.getScope()].add(p[1], p[2].typeList[0])
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
    for index_ in range(len(p[0].identList)):
        helper.symbolTables[helper.getScope()].add(p[0].identList[index_], p[0].typeList[index_])
    # TODO
    # Add the values from placeList in the code generation part, when the placeList[i] = 'nil', dont add any code

def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SEMICOLON
                              | epsilon'''
    p[0] = p[1]
    p[0].name = 'VarSpecRep'
    if len(p) == 4:
        p[0].identList += p[2].identList
        p[0].typeList += p[2].typeList
        p[0].placeList += p[2].placeList

def p_var_spec(p):
    '''VarSpec : IdentifierList Type ExpressionListOpt
                       | IdentifierList ASSIGN ExpressionList'''
    p[0] = p[1]
    p[0].name = 'VarSpec'
    if p[2] == '=':
        if len(p[1].identList) != len(p[3].typeList):
            err_ = str(len(p[1].identList)) + 'varaibles but ' + str(len(p[3].typeList)) + ' values'
            compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
        else:
            p[0].typeList = p[3].typeList
            p[0].placeList = p[3].placeList
    else:
        for i in range(len(p[1].identList)):
            p[0].typeList.append(p[2].typeList[0])
        if len(p[3].placeList) == 0:
            tmpArr = ['nil']
            p[0].placeList = tmpArr*len(p[0].identList)
        if len(p[3].placeList) != 0: # going to empty
            if len(p[0].identList) != len(p[3].placeList):
                err_ = str(len(p[0].identList)) + 'varaibles but ' + str(len(p[3].typeList)) + ' values'
                compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
                return
            for type_ in p[3].typeList:
                if type_ != p[2].typeList[0]:
                    err_ = type_ + ' assign to ' + p[2].typeList[0] 
                    compilation_errors.add('Type Mismatch', line_number.get()+1,err_)
                    return
            p[0].placeList = p[3].placeList

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
    p[0] = Node('ShortVarDecl')

    if helper.checkId(p[1],'current'):
        compilation_errors.add("Redeclare Error", line_number.get()+1,\
            "%s already declared"%p[1])
    else:
        helper.symbolTables[helper.getScope()].add(p[1],p[3].typeList[0])
        # newTemp = helper.newVar()
        # p[0].code - p[3].code
        # p[0].code.append(['=', newTemp, p[3].placelist[0]])
        # helper.symbolTables[helper.getScope()].update(p[1],'place',newTemp)
        # helper.symbolTables[helper.getScope()].update(p[1], 'type', p[3].typeList[0])
# -------------------------------------------------------




# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
    '''FunctionDecl : FUNC FunctionName Function
                                    | FUNC FunctionName Signature'''
    p[0] = Node('FunctionDecl')

def p_func_name(p):
    '''FunctionName : IDENT'''


def p_func(p):
    '''Function : Signature FunctionBody'''


def p_func_body(p):
    '''FunctionBody : Block'''
# -------------------------------------------------------


# ----------------------OPERAND----------------------------
def p_operand(p):
    '''Operand : BasicLit
                       | OperandName
                       | LPAREN Expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
    p[0].name = 'Operand'
    # TODO handle operandName

 # new rules start
def p_basic_lit(p):
    '''BasicLit : IntLit
                | FloatLit
                | StringLit
                '''
    p[0] = p[1]
    p[0].name = 'BasicLit'

def p_basic_lit_1(p):
    '''IntLit : INT_LITERAL'''
    p[0] = Node('IntLit')
    p[0].typeList.append('int')

def p_basic_lit_2(p):
    '''FloatLit : FLOAT_LITERAL'''
    p[0] = Node('FloatLit')
    p[0].typeList.append('float')

def p_basic_lit_3(p):
    '''StringLit : STRING_LITERAL'''
    p[0] = Node('StringLit')
    p[0].typeList.append('string')

# new rules finished

def p_operand_name(p):
    '''OperandName : IDENT'''
    p[0] = Node('OperandName')
    if not helper.checkId(p[1],'default'):
        compilation_errors.add('NameError', line_number.get()+1, '%s not declared'%p[1])
    else:
        type_ = helper.findInfo(p[1],'default')['type']
        p[0].typeList.append(type_)
    # TODO also place other things

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
    # Handling only operand
    if len(p)==2:
        p[0] = p[1]
    p[0].name = 'PrimaryExpr'


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

# ---------------------------------------------------------


# ----------------------OPERATORS-------------------------
def p_expr(p):
    '''Expression : UnaryExpr
                              | Expression BinaryOp Expression'''
    p[0] = Node('Expression')
    if len(p) == 2:
        p[0].typeList = p[1].typeList
        p[0].placeList = p[1].placeList
    else:
        # TODO typechecking
        newVar = helper.newVar()
        p[0].typeList = p[1].typeList
        p[0].placeList.append(newVar)

def p_expr_opt(p):
    '''ExpressionOpt : Expression
                                     | epsilon'''
    p[0] = Node('ExpressionOpt')
    p[0].typeList = p[1].typeList
    p[0].placeList = p[1].placeList

def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                             | UnaryOp UnaryExpr
                             | NOT UnaryExpr'''
    p[0] = Node('UnaryExpr')
    if len(p) == 2:
        p[0].typeList = p[1].typeList
        p[0].placeList = p[1].placeList
    elif p[1] == '!':
        p[0].typeList = p[2].typeList
        p[0].placeList = p[2].placeList
    else:
        p[0].typeList = p[2].typeList
        p[0].placeList = p[2].placeList


def p_binary_op(p):
    '''BinaryOp : LOR
                            | LAND
                            | RelOp
                            | AddMulOp'''
    p[0] = p[1]

def p_rel_op(p):
    '''RelOp : EQL
                     | NEQ
                     | LSS
                     | GTR
                     | LEQ
                     | GEQ'''
    p[0] = p[1]



def p_add_mul_op(p):
    '''AddMulOp : UnaryOp
                            | OR
                            | XOR
                            | QUO
                            | REM
                            | SHL
                            | SHR'''
    p[0] = p[1]


def p_unary_op(p):
    '''UnaryOp : ADD
                       | SUB
                       | MUL
                       | AND '''
    p[0] = p[1]

# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
    '''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
    p[0] = p[4]
    p[0].name = 'Conversion'
    tmpMap = helper.symbolTables[helper.getScope()].typeDefs
    type_ = p[2].typeList[0]
    if (type_ not in tmpMap) and (type_ not in size_mp):
       compilation_errors.add('TypeError',line_number.get()+1, "Type %s not defined"%type_) 
    else:
        p[0].typeList = p[2].typeList
        p[0].sizeList = p[2].sizeList
# ---------------------------------------------------------


# ---------------- STATEMENTS -----------------------
def p_statement(p):
    '''Statement : Declaration
                             | SimpleStmt
                             | ReturnStmt
                             | BreakStmt
                             | ContinueStmt
                             | Block
                             | IfStmt
                             | ForStmt '''



def p_simple_stmt(p):
    ''' SimpleStmt : epsilon
                                   | ExpressionStmt
                                   | IncDecStmt
                                   | Assignment
                                   | ShortVarDecl '''


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


def p_else_opt(p):
    ''' ElseOpt : ELSE IfStmt
                            | ELSE Block
                            | epsilon '''


# ----------------------------------------------------------------


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
    '''BreakStmt : BREAK'''


def p_continue(p):
    '''ContinueStmt : CONTINUE'''


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
    p[0] = p[2]
    p[0].name = 'PackageClause'



def p_package_name(p):
    '''PackageName : IDENT'''
    p[0] = Node('PackageName')
    p[0].identList.append(p[1])
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

# Debug here
helper.debug()

if compilation_errors.size() > 0:
    compilation_errors.printErrors()
    sys.exit(0)

out_file.write("}\n")
# Close file
out_file.close()
in_file.close()
