from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc
from lexer import *
from data_structures import Helper, Node
import json
import argparse
import sys

class DevNull:
    def write(self, msg):
        pass

sys.stderr = DevNull()

"""
CITE:
  Most of the token definations are taken from documentation
  of golang(go docs), and some from the token (go/token)
  package of golang: https://golang.org/src/go/token/token.go
"""

size_mp = {}
size_mp['float']   = 8
size_mp['int']     = 4
size_mp['bool']    = 1
size_mp['complex'] = 8
size_mp['string']  = 4
size_mp['pointer'] = 4

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
rootNode = Node('rootNode')
rootNode.code.append([helper.newLabel()])
helper.newScope()
# ------------------------START----------------------------


def p_start(p):
    '''start : SourceFile'''
    p[0] = p[1]
    p[0].name = 'start'
    global rootNode
    rootNode.code += p[0].code

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
        p[0].typeList.append([p[1]])
        p[0].sizeList.append(size_mp[p[1]])
    else:
        tmpMap = helper.findInfo(p[2])
        if tmpMap is None:
            compilation_errors.add('Type Error', line_number.get()+1, 'undefined: '+p[2])
        else:
            p[0].sizeList.append(tmpMap['size'])
            p[0].typeList.append([p[2]])

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
    p[0] = Node('ArrayType')
    if p[2].extra['count'] == -208016:
        # slice
        p[0].typeList.append(['slice', p[4].typeList[0], 0])
        p[0].sizeList.append(0)
    else:
        if p[2].extra['count'] < 0:
            compilation_errors.add('Size Error', line_number.get()+1, 'array bound must be non-negative')
            return
        p[0].typeList.append(['array', p[4].typeList[0], p[2].extra['count']])
        p[0].sizeList.append(int(p[2].extra['count']*p[4].sizeList[0]))
    p[0].name = 'ArrayType'

def p_array_length(p):
    ''' ArrayLength : INT_LITERAL
                            | epsilon'''
    p[0] = Node('ArrayLength')
    if isinstance(p[1], str):
        p[0].extra['count'] = int(p[1])
    else:
        p[0].extra['count'] = -208016
def p_element_type(p):
    ''' ElementType : Type '''
    p[0] = p[1]
    p[0].name = 'ElementType'

# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
    '''StructType : STRUCT LBRACE FieldDeclRep RBRACE'''
    p[0] = Node('StructType')
    for index_ in range(len(p[3].identList)):
        if p[3].identList[index_] in p[3].identList[:index_]:
            compilation_errors.add('Redeclaration Error',line_number.get()+1, 'Field %s redeclared'%p[3].identList[index_])
            return
    p[0] = p[3]
    dict_ = {}
    offset_ = 0
    for index_ in range(len(p[3].identList)):
        dict_[p[3].identList[index_]] = {'type':p[3].typeList[index_], 'size': p[3].sizeList[index_], 'offset':offset_}
        offset_ += p[3].sizeList[index_]
    p[0].typeList = [['struct', dict_]]
    p[0].sizeList = [sum(p[3].sizeList)]

def p_field_decl_rep(p):
    ''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
                                    | epsilon '''
    p[0] = p[1]
    p[0].name = 'FieldDeclRep'
    if len(p) == 4:
        p[0].identList += p[2].identList
        p[0].typeList += p[2].typeList
        p[0].sizeList += p[2].sizeList


def p_field_decl(p):
    ''' FieldDecl : IdentifierList Type'''
    p[0] = p[1]
    p[0].name = 'FieldDecl'

    p[0].typeList = [p[2].typeList[0]]*len(p[1].identList)
    p[0].sizeList = [p[2].sizeList[0]]*len(p[1].identList)

# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : MUL BaseType'''
    p[0] = Node('PointerType')
    p[0].typeList.append(['pointer', p[2].typeList[0]])
    p[0].sizeList.append(4)


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
    for index_ in range(len(p[0].identList)):
        helper.symbolTables[helper.getScope()].add(p[0].identList[index_], p[0].typeList[index_])
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'is_const', True)
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'offset', helper.getOffset())
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'size', p[0].sizeList[index_])
        helper.updateOffset(p[0].sizeList[index_])
    # TODO
    # Assign value to the constants in the code generation process.


def p_const_spec_rep(p):
    '''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
                                    | epsilon'''
    p[0] = p[1]
    p[0].name = 'ConstSpecRep'
    if len(p) == 4:
        p[0].identList += p[2].identList
        p[0].typeList += p[2].typeList
        p[0].placeList += p[2].placeList
        p[0].sizeList += p[2].sizeList
        p[0].code += p[2].code


def p_const_spec(p):
    '''ConstSpec : IdentifierList Type ASSIGN ExpressionList'''
    p[0] = p[1]
    p[0].code += p[4].code
    for i in range(len(p[1].identList)):
        p[0].typeList.append(p[2].typeList[0])
        p[0].sizeList.append(p[2].sizeList[0])
    if len(p[1].identList) != len(p[4].typeList):
        err_ = str(len(p[1].identList)) + ' constants but ' + str(len(p[4].typeList)) + ' values'
        compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
    for type_ in p[4].typeList:
        if type_ != p[2].typeList[0]:
            err_ = str(type_) + 'assigned to ' + str(p[2].typeList[0])
            compilation_errors.add('TypeMismatch', line_number.get()+1, err_)
    for idx_ in range(len(p[1].identList)):
        p[0].code.append(['=', p[1].identList[idx_], p[4].placeList[idx_]])
    p[0].placeList = p[4].placeList
    p[0].name = 'ConstSpec'

def p_identifier_list(p):
    '''IdentifierList : IDENT IdentifierRep'''
    p[0] = p[2]
    p[0].name = 'IdentifierList'

    if helper.checkId(p[1],'current') or (p[1] in p[2].identList):
        compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "%s already declared"%p[1])
    else:
        p[0].identList.insert(0,p[1])
        p[0].placeList.insert(0, p[1])


def p_identifier_rep(p):
    '''IdentifierRep : IdentifierRep COMMA IDENT
                                     | epsilon'''
    p[0] = p[1]
    p[0].name = 'IdentifierRep'
    if len(p) == 4:
        if helper.checkId(p[3], 'current') or (p[3] in p[0].identList):
            compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "%s already declared"%p[1])
        else:
            p[0].identList.append(p[3])


def p_expr_list(p):
    '''ExpressionList : Expression ExpressionRep'''
    p[0] = p[1]
    p[0].name = 'ExpressionList'
    p[0].placeList += p[2].placeList
    p[0].typeList += p[2].typeList
    p[0].sizeList += p[2].sizeList
    # TODO: understand addrlist
    p[0].code += p[2].code

def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                                     | epsilon'''

    p[0] = p[1]
    p[0].name = 'ExpressionRep'
    if len(p) == 4:
        p[0].code += p[3].code
        p[0].placeList += p[3].placeList
        p[0].typeList += p[3].typeList
        p[0].sizeList += p[3].sizeList
    # TODO: understand addrlist

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
    if len(p) == 2:
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
    p[0] = Node('AliasDecl')

    if helper.checkType(p[1],'current'):
        compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "Alias %s already declared"%p[1])
    else:
        helper.symbolTables[helper.getScope()].typeDefs[p[1]] = {'type': p[3].typeList[0], 'size': p[3].sizeList[0]}
        size_mp[p[1]] = p[3].sizeList[0]
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
    '''TypeDef : IDENT Type'''
    p[0] = Node('Typedef')

    if helper.checkType(p[1],'current'):
        compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "Type %s already declared"%p[1])
    else:
        helper.symbolTables[helper.getScope()].typeDefs[p[1]] = {'type': p[2].typeList[0], 'size': p[2].sizeList[0]}
        size_mp[p[1]] = p[2].sizeList[0]

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
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'offset', helper.getOffset())
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'size', p[0].sizeList[index_])
        helper.updateOffset(p[0].sizeList[index_])
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
        p[0].sizeList += p[2].sizeList
        p[0].code += p[2].code

def p_var_spec(p):
    '''VarSpec : IdentifierList Type ExpressionListOpt
                       | IdentifierList ASSIGN ExpressionList'''
    p[0] = p[1]
    p[0].code = p[3].code
    p[0].name = 'VarSpec'
    if p[2] == '=':
        if len(p[1].identList) != len(p[3].typeList):
            err_ = str(len(p[1].identList)) + ' varaibles but ' + str(len(p[3].typeList)) + ' values'
            compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
        else:
            p[0].typeList = p[3].typeList
            p[0].placeList = p[3].placeList
            p[0].sizeList = p[3].sizeList
            for idx_ in range(len(p[3].placeList)):
                p[0].code.append(['=', p[1].identList[idx_], p[3].placeList[idx_]])
    else:
        for i in range(len(p[1].identList)):
            p[0].typeList.append(p[2].typeList[0])
            p[0].sizeList.append(p[2].sizeList[0])

        if len(p[3].typeList) == 0:
            tmpArr = ['nil']
            p[0].placeList = tmpArr*len(p[0].identList)
        elif len(p[3].typeList) != 0: # not going to empty
            if len(p[0].identList) != len(p[3].typeList):
                err_ = str(len(p[0].identList)) + ' varaibles but ' + str(len(p[3].typeList)) + ' values'
                compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
                return
            for type_ in p[3].typeList:
                if type_ != p[2].typeList[0]:
                    err_ = str(type_) + ' assign to ' + str(p[2].typeList[0]) 
                    compilation_errors.add('TypeMismatch', line_number.get()+1,err_)
                    return
            p[0].placeList = p[3].placeList
            for idx_ in range(len(p[3].placeList)):
                p[0].code.append(['=', p[1].identList[idx_], p[3].placeList[idx_]])

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
        compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "%s already declared"%p[1])
    try:
        helper.symbolTables[helper.getScope()].add(p[1],p[3].typeList[0])
        helper.symbolTables[helper.getScope()].update(p[1], 'offset', helper.getOffset())
        helper.symbolTables[helper.getScope()].update(p[1], 'size', p[3].sizeList[0])
        helper.updateOffset(p[3].sizeList[0])
        p[0].code = p[3].code
        p[0].code.append(['=', p[1], p[3].placeList[0]])
    except:
        pass
# -------------------------------------------------------




# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
    '''FunctionDecl : FUNC FunctionName CreateScope Function EndScope
                                    | FUNC FunctionName CreateScope Signature EndScope'''
    p[0] = p[4]
    p[0].name = 'FunctionDecl'

def p_func_name(p):
    '''FunctionName : IDENT'''
    p[0] = Node('FunctionName')

def p_func(p):
    '''Function : Signature FunctionBody'''
    p[0] = p[2]
    p[0].name = 'Function'

def p_func_body(p):
    '''FunctionBody : Block'''
    p[0] = p[1]
    p[0].name = 'FunctionBody'

def p_create_scope(p):
    '''CreateScope : '''
    p[0] = Node('CreateScope')
    helper.newScope(helper.getScope())
    type_ = 'none'
    if isinstance(p[-1], str):
        type_ = p[-1]
    elif isinstance(p[-1], Node):
        if p[-1].name == 'FunctionName':
            type_ = 'func'
        
    label1 = helper.newLabel()
    label2 = helper.newLabel()
    label3 = helper.newLabel()
    label4 = helper.newLabel()
    helper.symbolTables[helper.getScope()].updateMetadata('start', label1)
    helper.symbolTables[helper.getScope()].updateMetadata('end', label2)
    helper.symbolTables[helper.getScope()].updateMetadata('name', type_)
    helper.symbolTables[helper.getScope()].updateMetadata('update',label3)
    helper.symbolTables[helper.getScope()].updateMetadata('condition', label4)
    

def p_delete_scope(p):
    '''EndScope : '''
    p[0] = Node('EndScope')
    for identifier in helper.symbolTables[helper.getScope()].typeDefs.keys():
        del size_mp[identifier]
    helper.endScope()
# ---------------------------------------------------------


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

 # new rules start
def p_basic_lit(p):
    '''BasicLit : IntLit
                | FloatLit
                | StringLit
                | BoolLit
                '''
    p[0] = p[1]
    p[0].name = 'BasicLit'

def p_basic_lit_1(p):
    '''IntLit : INT_LITERAL'''
    p[0] = Node('IntLit')
    p[0].typeList.append(['int'])
    newVar = helper.newVar(['int'], size_mp['int'])

    p[0].code.append(['=', newVar, p[1]])
    p[0].placeList.append(newVar)
    p[0].sizeList.append(size_mp['int'])

def p_basic_lit_2(p):
    '''FloatLit : FLOAT_LITERAL'''
    p[0] = Node('FloatLit')
    p[0].typeList.append(['float'])
    newVar = helper.newVar(['float'], size_mp['float'])
    p[0].code.append(['=', newVar, p[1]])
    p[0].placeList.append(newVar)
    p[0].sizeList.append(size_mp['float'])

def p_basic_lit_3(p):
    '''StringLit : STRING_LITERAL'''
    p[0] = Node('StringLit')
    p[0].typeList.append(['string'])
    newVar = helper.newVar(['string'], size_mp['string'])
    p[0].code.append(['=', newVar, p[1]])
    p[0].placeList.append(newVar)
    p[0].sizeList.append(size_mp['string'])

def p_basic_lit_4(p):
    '''BoolLit : TRUE
                    | FALSE'''
    p[0] = Node('BoolLit')
    p[0].typeList.append(['bool'])
    newVar = helper.newVar(['bool'], size_mp['bool'])
    p[0].code.append(['=', newVar, p[1]])
    p[0].placeList.append(newVar)
    p[0].sizeList.append(size_mp['bool'])

# new rules finished

def p_operand_name(p):
    '''OperandName : IDENT'''
    p[0] = Node('OperandName')
    if not helper.checkId(p[1],'default'):
        compilation_errors.add('NameError', line_number.get()+1, '%s not declared'%p[1])
    else:
        info_ = helper.findInfo(p[1],'default')
        p[0].typeList.append(info_['type'])
        p[0].placeList.append(p[1])
        p[0].sizeList.append(info_['size'])

# ---------------------------------------------------------



# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
    '''PrimaryExpr : Operand
                               | PrimaryExpr Selector
                               | Conversion
                               | PrimaryExpr Index
                               | PrimaryExpr Arguments'''
    # Handling only operand
    if len(p)==2:
        p[0] = p[1]
    elif p[2].name == 'Selector':
        p[0] = p[1]
        try:
            name_ = p[1].typeList[0][0]
            defn = helper.findInfo(name_)
            ident = p[2].extra['ident']
            if defn['type'][0] != 'struct':
                compilation_errors.add('TypeMismatch', line_number.get()+1, 'Before the period we must have struct type')
            elif ident not in defn['type'][1]:
                err_ = 'Name ' + name_ + ' has no field, or method called ' + ident
                compilation_errors.add('Field Error', line_number.get()+1, err_)
            else:
                # offset_ = defn['offset'] + defn['type'][1][ident]['offset']
                newVar1 = helper.newVar(defn['type'][1][ident]['type'],defn['type'][1][ident]['size'])
                p[0].code.append(['+', newVar1, p[1].placeList[0], defn['type'][1][ident]['offset']])
                p[0].placeList = ['*' + newVar1]
                p[0].sizeList = [defn['type'][1][ident]['size']]
                p[0].typeList = [defn['type'][1][ident]['type']]
                # TODO: store the offset of temporary also (needed in dereferencing)
        except:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Before period we must have struct')
    elif p[2].name == 'Index':
        p[0] = p[1]
        p[0].code += p[2].code
        if p[2].typeList[0] != ['int']:
            return # error handling already done in Index : rule
        elif not isinstance(p[1].typeList[0], list) or p[1].typeList[0][0] != 'array':
            compilation_errors.add('Invalid Operation', line_number.get()+1, 'type ' + str(p[1].typeList[0]) + ' does not support indexing')
        else:
            newVar1 = helper.newVar(p[1].typeList[0][1], size_mp[p[1].typeList[0][1][0]])
            p[0].code.append(['*', newVar1, p[2].placeList[0], size_mp[p[1].typeList[0][1][0]]])
            p[0].code.append(['+', newVar1, p[1].placeList[0], newVar1])
            p[0].placeList = ['*' + newVar1]
            p[0].sizeList = [size_mp[p[1].typeList[0][1][0]]]
            p[0].typeList = [p[1].typeList[0][1]]
    else:
        p[0] = p[1]
    # TODO: type checking for the remaining stuff
    p[0].name = 'PrimaryExpr'


def p_selector(p):
    '''Selector : PERIOD IDENT'''
    p[0] = Node('Selector')
    p[0].extra['ident'] = p[2]

def p_index(p):
    '''Index : LBRACK Expression RBRACK'''
    p[0] = p[2]
    p[0].name = 'Index'
    if p[2].typeList[0] != ['int']:
        compilation_errors.add('TypeError',line_number.get(), "Index type should be integer")

def p_argument(p):
    '''Arguments : LPAREN ExpressionListTypeOpt RPAREN'''
    p[0] = p[2]
    p[0].name = 'Arguments'


def p_expr_list_type_opt(p):
    '''ExpressionListTypeOpt : ExpressionList
                                                     | epsilon'''
    p[0] = p[1]
    p[0].name = 'ExpressionListTypeOpt'
# ---------------------------------------------------------


# ----------------------OPERATORS-------------------------
def p_expr(p):
    '''Expression : UnaryExpr
                              | Expression BinaryOp Expression'''
    p[0] = Node('Expression')
    if len(p) == 2:
        p[0].typeList = p[1].typeList
        p[0].placeList = p[1].placeList
        p[0].sizeList = p[1].sizeList
        p[0].code = p[1].code
    else:
        if p[1].typeList[0] != p[3].typeList[0]:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Type should be same across binary operator')
        elif p[1].typeList[0][0] not in p[2].extra:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Invalid type for binary expression')
        else:
            if len(p[2].typeList) > 0:
                # for boolean
                p[0].typeList = p[2].typeList
            else:
                p[0].typeList = p[1].typeList
            newVar = helper.newVar(p[0].typeList[0], p[1].sizeList[0])
            p[0].code = p[1].code
            p[0].code += p[3].code
            if len(p[2].extra) < 3:
                p[0].code.append([p[2].extra['opcode'], newVar, p[1].placeList[0], p[3].placeList[0]])
            else:
                p[0].code.append([p[2].extra['opcode'] + p[1].typeList[0][0], newVar, p[1].placeList[0], p[3].placeList[0]])
            p[0].sizeList = p[1].sizeList
            p[0].placeList.append(newVar)

def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                             | UnaryOp UnaryExpr
                             | NOT UnaryExpr'''
    p[0] = Node('UnaryExpr')
    if len(p) == 2:
        p[0].typeList = p[1].typeList
        p[0].placeList = p[1].placeList
        p[0].sizeList = p[1].sizeList
        p[0].code = p[1].code
    elif p[1] == '!':
        if p[2].typeList[0] != ['bool']:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Type should be boolean')
        else:
            p[0].typeList = p[2].typeList
            p[0].placeList = p[2].placeList
            p[0].sizeList = p[2].sizeList
            p[0].code = p[2].code
            newVar = helper.newVar(p[0].typeList[0], p[0].sizeList[0])
            p[0].code.append(['!', newVar, p[2].placeList[0]])
    else:
        if p[2].typeList[0][0] not in p[1].extra:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Invalid type for unary expression')
        else:
            p[0].typeList = p[2].typeList
            p[0].placeList = p[2].placeList
            p[0].sizeList = p[2].sizeList
            p[0].code = p[2].code
            newVar = helper.newVar(p[0].typeList[0], p[0].sizeList[0])
            p[0].code.append([p[1].extra['opcode'], newVar, p[2].placeList[0]])


def p_binary_op(p):
    '''BinaryOp : LOR
                            | LAND
                            | RelOp
                            | AddMulOp'''
    
    if isinstance(p[1], str):
        p[0] = Node('BinaryOp')
        p[0].extra['opcode'] = p[1]
        p[0].extra['bool'] = True
        p[0].typeList.append(['bool'])
    elif p[1].name == 'RelOp':
        p[0] = p[1]
        p[0].typeList.append(['bool'])
    else:
        p[0] = p[1]
    p[0].name = 'BinaryOp'

def p_rel_op(p):
    '''RelOp : EQL
                     | NEQ
                     | LSS
                     | GTR
                     | LEQ
                     | GEQ'''
    p[0] = Node('RelOp')
    p[0].extra['opcode'] = p[1]
    if p[1] in ['==', '!=']:
        p[0].extra['bool'] = True
        p[0].extra['int'] = True
        p[0].extra['string'] = True
        p[0].extra['float'] = True
    else:
        p[0].extra['int'] = True 
        p[0].extra['float'] = True 
        p[0].extra['string'] = True 


def p_add_mul_op(p):
    '''AddMulOp : UnaryOp
                            | OR
                            | XOR
                            | QUO
                            | REM
                            | SHL
                            | SHR'''
    if isinstance(p[1], str):
        p[0] = Node('AddMulOp')
        p[0].extra['opcode'] = p[1]
        p[0].extra['int'] = True
        if p[1] == '/':
            p[0].extra['float'] = True
    else:
        p[0] = p[1]
        p[0].name = 'AddMulOp'

def p_unary_op(p):
    '''UnaryOp : ADD
                       | SUB
                       | MUL
                       | AND '''
    p[0] = Node('UnaryOp')
    p[0].extra['int'] = True
    p[0].extra['float'] = True
    p[0].extra['string'] = True
    p[0].extra['opcode'] = p[1]

# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
    '''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
    p[0] = p[4]
    newVar = helper.newVar(p[2].typeList[0], p[2].sizeList[0])
    p[0].code.append(['=', newVar, '(' + str(p[2].typeList[0]) + ')' + str(p[4].placeList[0])])
    p[0].name = 'Conversion'
    p[0].placeList = [newVar]
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
                             | CreateScope Block EndScope
                             | IfStmt
                             | ForStmt '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
    p[0].name = 'Statement'


def p_simple_stmt(p):
    ''' SimpleStmt : epsilon
                                   | ExpressionStmt
                                   | IncDecStmt
                                   | Assignment
                                   | ShortVarDecl '''
    p[0] = p[1]
    p[0].name = 'SimpleStmt'


def p_expression_stmt(p):
    ''' ExpressionStmt : Expression '''
    p[0] = p[1]
    p[0].name = 'ExpressionStmt'


def p_inc_dec(p):
    ''' IncDecStmt : Expression INC
                                   | Expression DEC '''
    p[0] = p[1]
    p[0].name = 'IncDecStmt'
    if  p[1].typeList[0] != ['int']:
        err_ = str(p[1].typeList[0]) + 'cannot be incremented/decremented'
        compilation_errors.add('TypeMismatch', line_number.get()+1, err_)
    newVar = helper.newVar(['int'], size_mp['int'])
    p[0].code.append([p[2], newVar, p[1].placeList[0]])

def p_assignment(p):
    ''' Assignment : ExpressionList assign_op ExpressionList'''
    p[0] = p[1]
    if len(p[1].typeList) != len(p[3].placeList):
        err_ = str(len(p[1].typeList)) + ' identifier on left, while ' + str(len(p[3].placeList)) + ' expression on right'
        compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
    else:
        for index_,type_ in enumerate(p[3].typeList):
            info = helper.findInfo(p[1].placeList[index_])
            bool_ = True
            try:
                tp_3 = helper.findInfo(type_[0])
                if tp_3['type'] == p[1].typeList[index_]:
                    bool_ = False
            except:
                pass
            try:
                tp_1 = helper.findInfo(p[1].typeList[index_][0])
                if tp_1['type'] == type_:
                    bool_ = False
            except:
                pass
            try:
                tp_1 = helper.findInfo(p[1].typeList[index_][0])
                tp_3 = helper.findInfo(type_[0])
                if tp_1['type'] == tp_3['type']:
                    bool_ = False
            except:
                pass
            if info is None:
                info = []
            if 'is_const' in info:
                compilation_errors.add('ConstantAssignment', line_number.get()+1, 'Constant cannot be reassigned')
            elif (type_ != p[1].typeList[index_]) and bool_:
                err_ = str(type_) + ' assigned to ' + str(p[1].typeList[index_])
                compilation_errors.add('TypeMismatch', line_number.get()+1, err_)
            elif type_[0] not in p[2].extra:
                compilation_errors.add('TypeMismatch', line_number.get()+1, 'Invalid Type for operator %s'%p[2].extra['opcode'])
    p[0].name = 'Assignment'
    p[0].code += p[3].code
    for idx_ in range(len(p[3].typeList)):
        p[0].code.append([p[2].extra['opcode'], p[1].placeList[idx_], p[3].placeList[idx_]])

def p_assign_op(p):
    ''' assign_op : AssignOp'''
    p[0] = p[1]
    p[0].name = 'assign_op'


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
    p[0] = Node('AssignOp')
    p[0].extra['opcode'] = p[1]
    if p[1] == '=':
        p[0].extra['bool'] = True
        p[0].extra['int'] = True
        p[0].extra['string'] = True
        p[0].extra['float'] = True
    else:
        p[0].extra['int'] = True

def p_if_statement(p):
    ''' IfStmt : IF CreateScope Expression Block ElseOpt EndScope'''
    p[0] = p[3]
    if p[3].typeList[0] != ['bool']:
        compilation_errors.add('TypeError',line_number.get()+1, 'Non-bool expression (%s) used as if condition'%p[3].typeList[0])
    # if x relopy gotoL
    newLabel1 = helper.newLabel()
    p[0].code.append(['if',p[3].placeList[0],'==','False', 'goto',newLabel1])
    p[0].code += p[4].code
    newLabel2 = helper.newLabel()
    p[0].code.append(['goto', newLabel2])
    p[0].code.append([newLabel1])
    p[0].code += p[5].code
    p[0].code.append([newLabel2])

def p_else_opt(p):
    ''' ElseOpt : ELSE CreateScope IfStmt EndScope
                            | ELSE CreateScope Block EndScope
                            | epsilon '''
    if len(p)==2:
        p[0] = p[1]
        p[0].extra['isEmpty'] = True
    else:
        p[0] = p[3]
    p[0].name = 'ElseOpt'


# ----------------------------------------------------------------


# -----------------------------------------------------------


# --------- FOR STATEMENTS AND OTHERS (MANDAL) ---------------
def p_for(p):
    '''ForStmt : FOR CreateScope ConditionBlockOpt Block EndScope'''
    p[0] = p[3]
    start = helper.symbolTables[helper.lastScope].metadata['start']
    update = helper.symbolTables[helper.lastScope].metadata['update']
    end = helper.symbolTables[helper.lastScope].metadata['end']
    p[0].code += [[start]]
    p[0].code += p[4].code
    p[0].code += [['goto', update]]
    p[0].code += [[end]]
    p[0].name = 'ForStmt'


def p_conditionblockopt(p):
    '''ConditionBlockOpt : epsilon
                           | Condition
                           | ForClause'''
    
    p[0] = p[1]
    condition = helper.symbolTables[helper.getScope()].metadata['condition']
    update = helper.symbolTables[helper.getScope()].metadata['update']
    if p[1].name != 'ForClause':
        p[0].code.insert(0, [condition])
    if p[1].name == 'epsilon':
        p[0].extra['isInfinite'] = True
        p[0].code += [[update]]
    p[0].name = 'ConditionBlockOpt'


def p_condition(p):
    '''Condition : Expression'''
    p[0] = p[1]
    end = helper.symbolTables[helper.getScope()].metadata['end']
    p[0].code.append(['if', p[1].placeList[0], '==', 'False', 'goto', end])
    if p[1].typeList[0] != ['bool']:
        compilation_errors.add('TypeMismatch', line_number.get()+1, 'Expression type should be bool')
    p[0].name = 'Condition'
    update = helper.symbolTables[helper.getScope()].metadata['update']


def p_forclause(p):
    '''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
    p[0] = p[1]
    condition = helper.symbolTables[helper.getScope()].metadata['condition']
    update = helper.symbolTables[helper.getScope()].metadata['update']
    start = helper.symbolTables[helper.getScope()].metadata['start']
    p[0].code += [[condition]]
    p[0].code += p[3].code
    p[0].code += [['goto', start]]
    p[0].code += [[update]]
    p[0].code += p[5].code
    p[0].code += [['goto', condition]]
    p[0].name = 'ForClause'

    p[0].extra = p[3].extra


def p_conditionopt(p):
    '''ConditionOpt : epsilon
                    | Condition'''
    p[0] = p[1]
    p[0].name = 'ConditionOpt'
    if p[1].name == 'epsilon':
        p[0].extra['isInfinite'] = True



def p_return(p):
    '''ReturnStmt : RETURN ExpressionListPureOpt'''
    p[0] = Node('ReturnStmt')
    # TODO: return data should also be handled
    scope_ = helper.getNearest('func')
    if scope_ == -1:
        compilation_errors.add('Scope Error', line_number.get()+1, 'return is not in a function')
        return
    symTab = helper.symbolTables[scope_]
    p[0].code = [['goto', symTab.metadata['end']]]
    # TODO:  this should not be end, return label must be given before



def p_expressionlist_pure_opt(p):
    '''ExpressionListPureOpt : ExpressionList
                           | epsilon'''
    p[0] = p[1]
    p[0].name = 'ExpressionListPureOpt'

def p_break(p):
    '''BreakStmt : BREAK'''
    p[0] = Node('BreakStmt')
    scope_ = helper.getNearest('for')
    if scope_ == -1:
        compilation_errors.add('Scope Error', line_number.get()+1, 'break is not in a loop')
        return
    symTab = helper.symbolTables[scope_]
    p[0].code = [['goto', symTab.metadata['end']]]

def p_continue(p):
    '''ContinueStmt : CONTINUE'''
    p[0] = Node('ContinueStmt')
    scope_ = helper.getNearest('for')
    if scope_ == -1:
        compilation_errors.add('Scope Error', line_number.get()+1, 'continue is not in a loop')
        return
    symTab = helper.symbolTables[scope_]
    p[0].code = [['goto', symTab.metadata['update']]]

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
    p[0] = p[1]
    p[0].name = 'TopLevelDeclRep'
    if len(p) != 2:
        p[0].code += p[2].code


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

def getCodeString(codeList):
    len_ = len(codeList)
    tmpList = []
    for x in codeList:
        tmpList.append(str(x))
    codeList = tmpList
    if len_ == 0:
        return ''
    elif len_ == 1:
        return codeList[0] + ':'
    elif len_ == 2:
        return '    goto: ' + codeList[1]
    elif len_ == 3:
        op = codeList[0]
        if op == '=':
            operand_ = codeList[2]
            if codeList[2][0] in ['&', '*']:
                operand_ = codeList[2][0] + '(' + codeList[2][1:] + ')'
            return '    ' + codeList[1] + ' = ' + operand_
        elif op == '!':
            return '    ' + codeList[1] + ' = !(' + codeList[2] + ')'
        elif op == '++':
            return '    ' + codeList[1] + ' = ' + codeList[2] + ' +int 1'
        elif op == '--':
            return '    ' + codeList[1] + ' = ' + codeList[2] + ' -int 1'
        elif len(op) == 2 and (op[1] == '=' and op[0] not in ['=', '!', ':', '>', '<']):
            return '    ' + codeList[1] + ' = ' + codeList[1] + ' ' + op[0] + ' ' + codeList[2]
        elif len(op) == 3:
            return '    ' + codeList[1] + ' = ' + codeList[1] + ' ' + op[0:2] + ' ' + codeList[2]
        else:
            return '    ' + codeList[1] + ' ' + codeList[0] + ' ' + codeList[2]
    elif len_ == 4:
        return '    ' + codeList[1] + ' = ' + codeList[2] + ' ' + codeList[0] + ' ' + codeList[3]
    else:
        str_ = '    '
        for x in codeList:
            str_ += (x + ' ')
        return str_

def generateCSV(filename):
    import csv
    csvfile = filename
    writer = csv.writer(csvfile)

    writer.writerow(['-------', '-------', '-------','------','------'])
    writer.writerow(['Identifier', 'Type', 'Size','Offset','is_Constant'])
    writer.writerow(['-------', '-------', '-------','------','------'])

    for idx_, table in enumerate(helper.symbolTables):
        # create rows
        writer.writerow(['','','','',''])
        writer.writerow(['======','Symbol Table Number:'+ str(idx_),'======','======','======'])
        writer.writerow(['','','','',''])

        symTable = table.table
        ident = symTable.keys()
        type_ = [symTable[key]['type'] for key in ident]
        size_ = [symTable[key]['size'] for key in ident]
        offset_ = [symTable[key]['offset'] for key in ident]
        is_const = ['is_const' in symTable[key] for key in ident]
        rows = []
        for idx_,key in enumerate(ident):
            row = [key,type_[idx_],size_[idx_],offset_[idx_],is_const[idx_]]
            rows.append(row)
        writer.writerows(rows)

        writer.writerow(['','','','',''])
        writer.writerow(['======','======','======','======','======'])
        writer.writerow(['','','','',''])

parser = argparse.ArgumentParser(description='Does Semantic Analysis and generates 3AC')

parser.add_argument('--code', dest='code_file_location', help='Location of the output .code file for 3AC', required=True)

parser.add_argument('--csv', dest='csv_file_location', help='Location of the output .csv file for symbol tables', required=True)

parser.add_argument('--input', dest='in_file_location', help='Location of the input .go file', required=True)

parser.add_argument('--debug', dest='isDebug', help='for dubugging mode [t/F]', required=False)

result = parser.parse_args()
code_file_location = str(result.code_file_location)
csv_file_location = str(result.csv_file_location)
in_file_location = str(result.in_file_location)
isDebug = str(result.isDebug)


# Build lexer
lexer = lex.lex()

# Read input file
in_file = open(in_file_location,'r')


# CSV output File
csv_file = open(csv_file_location,"w+")

# 3AC output file
code_file = open(code_file_location,"w+")

data = in_file.read()

# Iterate to get tokens
parser = yacc.yacc()
res = parser.parse(data)

# Dubug Mode
if isDebug in ['true', 't','T','True']:
    helper.debug()

if compilation_errors.size() > 0:
    sys.exit()
generateCSV(csv_file)

for idx_ in range(len(rootNode.code)):
    code_file.write(getCodeString(rootNode.code[idx_]))
    code_file.write('\n')

code_file.close()
in_file.close()
