from ply import lex
from ply.lex import TOKEN
import ply.yacc as yacc
from lexer import *
from data_structures import Helper, Node
import json
import argparse
import sys

# class DevNull:
#     def write(self, msg):
#         pass

# sys.stderr = DevNull()

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
rootNode = Node('rootNode')
helper.newScope()
# ------------------------START----------------------------


def p_start(p):
    '''start : SourceFile'''
    p[0] = p[1]
    p[0].name = 'start'
    global rootNode
    rootNode.code += p[0].code
    rootNode.scopeInfo += p[0].scopeInfo

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
    else:
        if not helper.checkType(p[2]):
            compilation_errors.add('Type Error', line_number.get()+1, 'undefined: '+p[2])
        else:
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
    p[0] = Node('ArrayType')
    if p[2].extra['count'] == -208016:
        # slice
        newSlice = helper.addUnNamedType(['slice', {
            'type': helper.getBaseType(p[4].typeList[0]),
            'len':  0
        }])
        p[0].typeList.append(newSlice)
    else:
        if p[2].extra['count'] < 0:
            compilation_errors.add('Size Error', line_number.get()+1, 'array bound must be non-negative')
            return
        newArr = helper.addUnNamedType(['array', {
            'type': helper.getBaseType(p[4].typeList[0]),
            'len':  p[2].extra['count']
        }])
        p[0].typeList.append(newArr)
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
    '''StructType : STRUCT LBRACE structInit FieldDeclRep RBRACE structDeInit'''
    p[0] = Node('StructType')
    for index_ in range(len(p[4].identList)):
        if p[4].identList[index_] in p[4].identList[:index_]:
            compilation_errors.add('Redeclaration Error',line_number.get()+1, 'Field %s redeclared'%p[4].identList[index_])
            return
    p[0] = p[4]
    dict_ = {}
    offset_ = 0
    for index_ in range(len(p[4].identList)):
        baseType = helper.getBaseType(p[4].typeList[index_])
        sz = helper.computeSize(baseType)
        dict_[p[4].identList[index_]] = {
            'type': baseType,
            'size': sz,
            'offset':offset_
        }
        offset_ += sz
    newStruct = helper.addUnNamedType(['struct', dict_])
    p[0].typeList = [newStruct]

    p[0].name = 'StructType'

def p_structInit(p):
    '''structInit : epsilon'''
    helper.type[p[-3]] = {'type': ['struct', p[-3]], 'size': 0}

def p_structDeInit(p):
    '''structDeInit : epsilon'''
    helper.type.pop(p[-6], None)

def p_field_decl_rep(p):
    ''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
                                    | epsilon '''
    p[0] = p[1]
    p[0].name = 'FieldDeclRep'
    if len(p) == 4:
        p[0].identList += p[2].identList
        p[0].typeList += p[2].typeList


def p_field_decl(p):
    ''' FieldDecl : IdentifierList Type'''
    p[0] = p[1]
    p[0].name = 'FieldDecl'

    p[0].typeList = [p[2].typeList[0] for x in p[1].identList]

# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : MUL BaseType'''
    p[0] = Node('PointerType')
    baseTp = helper.getBaseType(p[2].typeList[0])
    newPointer = helper.addUnNamedType(['pointer', baseTp])
    p[0].typeList.append(newPointer)


def p_base_type(p):
    '''BaseType : Type'''
    p[0] = p[1]
    p[0].name = 'BaseType'

# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
    '''Signature : LPAREN ParameterListOpt RPAREN ResultOpt'''
    # update the parameters in the function scope
    p[0] = Node('Signature')
    # Doubt: this shouldn't be p[2].typeList[0]
    # we store it as a list since we need to handle void functions as well.
    msg = helper.updateSignature(p[2].typeList)
    if msg != 'cool':
        compilation_errors.add('Redeclaration Error', line_number.get()+1, msg)
        return
    helper.updateRetValType(p[4].typeList)

    retValSize = []
    for x in p[4].typeList:
        retValSize.append(helper.type[x]['size'])
    helper.updateSize(retValSize)

def p_result_opt(p):
    '''ResultOpt : Type
                             | epsilon'''
    p[0] = Node('ResultOpt')
    if p[1].name != 'epsilon':
        p[0] = p[1]
        p[0].name = 'ResultOpt'

def p_param_list_opt(p):
    '''ParameterListOpt : ParameterDeclCommaRep
                                                     | epsilon'''
    p[0] = Node('ParameterListOpt')
    if p[1].name != 'epsilon':
        p[0] = p[1]
        p[0].name = 'ParameterListOpt'
        for index_ in range(len(p[1].typeList)):
            sz = helper.getSize(p[1].typeList[index_])
            helper.symbolTables[helper.getScope()].add(p[1].identList[index_], p[1].typeList[index_])
            helper.symbolTables[helper.getScope()].update(p[1].identList[index_], 'size', sz)
            helper.symbolTables[helper.getScope()].update(p[1].identList[index_], 'offset', helper.getOffset())
            helper.symbolTables[helper.getScope()].update(p[1].identList[index_], 'is_arg', True)
            helper.updateOffset(sz)

def p_param_decl_comma_rep(p):
    '''ParameterDeclCommaRep : ParameterDeclCommaRep COMMA ParameterDecl
                                                     | ParameterDecl'''
    if len(p) == 2:
        p[0] = p[1]
        p[0].name = 'ParameterDeclCommaRep'
    else:
        p[0] = p[1]
        p[0].placeList += p[3].placeList
        p[0].identList += p[3].identList
        p[0].typeList += p[3].typeList


def p_param_decl(p):
    '''ParameterDecl : IDENT Type '''
    p[0] = Node('ParameterDecl')
    p[0].placeList = [p[1]]
    p[0].identList = [p[1]]
    p[0].typeList = p[2].typeList

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
        p[0].scopeInfo += p[2].scopeInfo

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
        sz = helper.getSize(p[0].typeList[index_])
        helper.symbolTables[helper.getScope()].add(p[0].identList[index_], p[0].typeList[index_])
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'is_const', True)
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'offset', helper.getOffset())
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'size', sz)
        helper.updateOffset(sz)


def p_const_spec_rep(p):
    '''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
                                    | epsilon'''
    p[0] = p[1]
    p[0].name = 'ConstSpecRep'
    if len(p) == 4:
        p[0].identList += p[2].identList
        p[0].typeList += p[2].typeList
        p[0].placeList += p[2].placeList
        p[0].code += p[2].code
        p[0].scopeInfo += p[2].scopeInfo

def p_const_spec(p):
    '''ConstSpec : IdentifierList Type ASSIGN ExpressionList'''
    p[0] = p[1]
    p[0].code += p[4].code
    p[0].scopeInfo += p[4].scopeInfo
    for i in range(len(p[1].identList)):
        p[0].typeList.append(p[2].typeList[0])
    if len(p[1].identList) != len(p[4].typeList):
        err_ = str(len(p[1].identList)) + ' constants but ' + str(len(p[4].typeList)) + ' values'
        compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
    for type_ in p[4].typeList:
        if not helper.compareType(type_, p[2].typeList[0]):
            err_ = str(type_) + 'assigned to ' + str(p[2].typeList[0])
            compilation_errors.add('TypeMismatch', line_number.get()+1, err_)
    for idx_ in range(len(p[1].identList)):
        p[0].code.append(['=', p[1].identList[idx_], p[4].placeList[idx_]])
        p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[4].placeList[idx_])])
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
            p[0].placeList.append(p[3])


def p_expr_list(p):
    '''ExpressionList : Expression ExpressionRep'''
    p[0] = p[1]
    p[0].name = 'ExpressionList'
    p[0].placeList += p[2].placeList
    p[0].typeList += p[2].typeList
    p[0].code += p[2].code
    p[0].extra['deref'] += p[2].extra['deref']
    p[0].scopeInfo += p[2].scopeInfo

def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                                     | epsilon'''

    p[0] = p[1]
    p[0].name = 'ExpressionRep'
    if len(p) == 4:
        p[0].code += p[3].code
        p[0].scopeInfo += p[3].scopeInfo
        p[0].placeList += p[3].placeList
        p[0].typeList += p[3].typeList
        p[0].extra['deref'] += p[3].extra['deref']
    else:
        p[0].extra['deref'] = []

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

    if helper.checkType(p[1]):
        compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "Alias %s already declared"%p[1])
    else:
        helper.type[p[1]] = helper.type[p[3].typeList[0]]
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
    '''TypeDef : IDENT Type'''
    p[0] = Node('Typedef')

    if helper.checkType(p[1]):
        compilation_errors.add("Redeclaration Error", line_number.get()+1,\
            "Type %s already declared"%p[1])
    else:
        helper.type[p[1]] = helper.type[p[2].typeList[0]]
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
        sz = helper.getSize(p[0].typeList[index_])
        helper.symbolTables[helper.getScope()].add(p[0].identList[index_], p[0].typeList[index_])
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'offset', helper.getOffset())
        helper.symbolTables[helper.getScope()].update(p[0].identList[index_], 'size', sz)
        helper.updateOffset(sz)

def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SEMICOLON
                              | epsilon'''
    p[0] = p[1]
    p[0].name = 'VarSpecRep'
    if len(p) == 4:
        p[0].identList += p[2].identList
        p[0].typeList += p[2].typeList
        p[0].placeList += p[2].placeList
        p[0].code += p[2].code
        p[0].scopeInfo += p[2].scopeInfo

def p_var_spec(p):
    '''VarSpec : IdentifierList Type ExpressionListOpt
                       | IdentifierList ASSIGN ExpressionList'''
    p[0] = p[1]
    p[0].code = p[3].code
    p[0].scopeInfo = p[3].scopeInfo
    p[0].name = 'VarSpec'
    if p[2] == '=':
        if len(p[1].identList) != len(p[3].typeList):
            err_ = str(len(p[1].identList)) + ' varaibles but ' + str(len(p[3].typeList)) + ' values'
            compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
        else:
            p[0].typeList = p[3].typeList
            p[0].placeList = p[3].placeList
            for idx_ in range(len(p[3].placeList)):
                p[0].code.append(['=', p[1].identList[idx_], p[3].placeList[idx_]])
                p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[3].placeList[idx_])])
    else:
        for i in range(len(p[1].identList)):
            p[0].typeList.append(p[2].typeList[0])

        if len(p[3].typeList) != 0: # not going to empty
            if len(p[0].identList) != len(p[3].typeList):
                err_ = str(len(p[0].identList)) + ' varaibles but ' + str(len(p[3].typeList)) + ' values'
                compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
                return
            for type_ in p[3].typeList:
                if not helper.compareType(type_, p[2].typeList[0]):
                    err_ = str(type_) + ' assign to ' + str(p[2].typeList[0])
                    compilation_errors.add('TypeMismatch', line_number.get()+1,err_)
                    return
            p[0].placeList = p[3].placeList
            for idx_ in range(len(p[3].placeList)):
                p[0].code.append(['=', p[1].identList[idx_], p[3].placeList[idx_]])
                p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[3].placeList[idx_])])

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
        sz = helper.getSize(p[3].typeList[0])
        helper.symbolTables[helper.getScope()].add(p[1],p[3].typeList[0])
        helper.symbolTables[helper.getScope()].update(p[1], 'offset', helper.getOffset())
        helper.symbolTables[helper.getScope()].update(p[1], 'size', sz)
        helper.updateOffset(sz)
        p[0].code = p[3].code
        p[0].scopeInfo = p[3].scopeInfo
        p[0].code.append(['=', p[1], p[3].placeList[0]])
        p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[3].placeList[0])])
    except:
        pass
# -------------------------------------------------------




# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
    '''FunctionDecl : FUNC FunctionName CreateScope Function EndScope '''

    p[0] = p[4]
    p[0].name = 'FunctionDecl'
    funcScope = helper.symbolTables[0].functions[p[2].extra['name']][-1]
    if 'is_empty' not in p[4].extra:
        if p[2].extra['name'] in helper.symbolTables[0].maybe:
            newfuncScope = helper.symbolTables[0].maybeScope[p[2].extra['name']]
            p[0].code.insert(0,[p[2].extra['name']+str(newfuncScope)+'::'])  
            p[0].scopeInfo.insert(0,[''])
            helper.symbolTables[0].functions[p[2].extra['name']+str(newfuncScope)] = funcScope
        else:  
            p[0].code.insert(0,[p[2].extra['name']+str(funcScope)+'::'])
            p[0].scopeInfo.insert(0,[''])
            helper.symbolTables[0].functions[p[2].extra['name']+str(funcScope)] = funcScope
    else:
        helper.symbolTables[0].maybe.append(p[2].extra['name'])
        helper.symbolTables[0].maybeScope[p[2].extra['name']] = funcScope

def p_func_name(p):
    '''FunctionName : IDENT'''
    p[0] = Node('FunctionName')
    p[0].extra['name'] = p[1]
    helper.addFunc(p[1])

def p_func(p):
    '''Function : Signature FunctionBody'''
    p[0] = p[2]
    p[0].name = 'Function'

def p_func_body(p):
    '''FunctionBody : Block
                    | epsilon'''
    p[0] = p[1]
    if p[1].name == 'epsilon':
        p[0].extra['is_empty'] = True
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
            helper.makeSymTabFunc(p[-1].extra['name'])

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
    p[0].typeList.append('int')
    newVar = helper.newVar('int')

    p[0].code.append(['=', newVar, int(p[1])])
    p[0].scopeInfo.append(['', helper.getScope() , 'int_literal'])
    p[0].placeList.append(newVar)

def p_basic_lit_2(p):
    '''FloatLit : FLOAT_LITERAL'''
    p[0] = Node('FloatLit')
    p[0].typeList.append('float')
    newVar = helper.newVar('float')
    p[0].code.append(['=', newVar, float(p[1])])
    p[0].scopeInfo.append(['', helper.getScope() , 'literal'])
    p[0].placeList.append(newVar)

def p_basic_lit_3(p):
    '''StringLit : STRING_LITERAL'''
    p[0] = Node('StringLit')
    p[0].typeList.append('string')
    newVar = helper.newVar('string')
    p[0].code.append(['=', newVar, p[1]])
    p[0].scopeInfo.append(['', helper.getScope() , 'literal'])
    p[0].placeList.append(newVar)

def p_basic_lit_4(p):
    '''BoolLit : TRUE
                    | FALSE'''
    p[0] = Node('BoolLit')
    p[0].typeList.append('bool')
    newVar = helper.newVar('bool')
    p[0].code.append(['=', newVar, p[1]])
    p[0].scopeInfo.append(['', helper.getScope() , 'literal'])
    p[0].placeList.append(newVar)

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

# ---------------------------------------------------------


# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
    '''PrimaryExpr : Operand
                               | PrimaryExpr Selector
                               | Conversion
                               | PrimaryExpr Index
                               | IDENT Arguments'''
    # Handling only operand
    if len(p)==2:
        p[0] = p[1]
    elif p[2].name == 'Selector':
        p[0] = p[1]
        if True:
            baseType = helper.getBaseType(p[1].typeList[0])
            ident = p[2].extra['ident']
            if isinstance(baseType[1], str):
                baseType[1] = helper.getBaseType(baseType[1])[1]
            if baseType[0] != 'struct':
                compilation_errors.add('TypeMismatch', line_number.get()+1, 'Before the period we must have struct type')
            elif ident not in baseType[1]:
                err_ = 'Name ' + str(baseType[1]) + ' has no field, or method called ' + ident
                compilation_errors.add('Field Error', line_number.get()+1, err_)

            else:
                identType = helper.addUnNamedType(baseType[1][ident]['type'])
                newVar1 = helper.newVar('int')
                helper.symbolTables[helper.getScope()].update(newVar1, 'type', identType)
                p[0].code.append(['+int', newVar1, p[1].placeList[0], baseType[1][ident]['offset']])
                p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[1].placeList[0]), 'offset'])
                p[0].placeList = [newVar1]
                p[0].identList = p[0].placeList
                p[0].typeList = [identType]
                helper.symbolTables[helper.getScope()].update(newVar1, 'reference', True)
        else:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Before period we must have struct')

    elif p[2].name == 'Index':
        p[0] = p[1]
        p[0].code += p[2].code
        p[0].scopeInfo += p[2].scopeInfo
        rawType = helper.getBaseType(p[1].typeList[0])
        if not helper.compareType(p[2].typeList[0], 'int'):
            return # error handling already done in Index : rule
        elif rawType[0] != 'array' and rawType[0] != 'pointer':
            compilation_errors.add('Invalid Operation', line_number.get()+1, 'type ' + str(helper.getBaseType(p[1].typeList[0])) + ' does not support indexing')
        else:
            arrayElemtp = helper.addUnNamedType(rawType[1]['type'])
            newVar1 = helper.newVar('int')
            helper.symbolTables[helper.getScope()].update(newVar1, 'type', arrayElemtp)
            newVar2 = helper.newVar('int')
            arrayElemSz = helper.type[arrayElemtp]['size']
            p[0].code.append(['*' + 'int', newVar2, p[2].placeList[0], arrayElemSz])
            p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[2].placeList[0]), 'literal'])
            p[0].code.append(['+' + 'int', newVar1, p[1].placeList[0], newVar2])
            p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[1].placeList[0]), helper.getScope()])
            p[0].placeList = [newVar1]
            p[0].typeList = [arrayElemtp]
            helper.symbolTables[helper.getScope()].update(newVar1, 'reference', True)
            p[0].extra['isIndex'] = True

    elif p[2].name == 'Arguments':
        p[0] = p[2]
        msg = helper.checkArguments(p[1],p[2].typeList)
        if msg[0] == 'a':
            compilation_errors.add('Type Error',line_number.get()+1, msg)
        else:
            funcScope = int(msg)
            if funcScope == -1:
                compilation_errors.add('Declaration Error', line_number.get()+1, 'Function %s not defined'%p[1])
            else:
                for arg in p[2].placeList:
                    p[0].code.append(['param', arg])
                    p[0].scopeInfo.append(['', helper.findScope(arg)])
                p[0].code.append(['call', p[1] + str(funcScope), len(p[2].placeList)])
                p[0].scopeInfo.append(['', 'function', 'int'])
                type_ = helper.getRetType(funcScope)
                size_ = helper.getRetSize(funcScope)
                p[0].typeList = type_
                newVar1 = helper.newVar(type_)
                p[0].code.append(['retval', newVar1, 'eax'])
                p[0].scopeInfo.append(['', helper.findScope(newVar1), ''])
                argList = ''
                for arg in p[2].placeList:
                    argList += str(arg) + ', '
                argList = argList[:-2]
                p[0].identList = [newVar1]
                p[0].sizeList = size_
                p[0].placeList = p[0].identList
                # TODO: see what can be there
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
    if not helper.compareType(p[2].typeList[0], 'int'):
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
        p[0].code = p[1].code
        p[0].scopeInfo = p[1].scopeInfo
        p[0].extra['deref'] = p[1].extra['deref']
        p[0].extra['scope'] = helper.getScope()
    else:
        p[0].extra['deref'] = ['no']
        tp = helper.getBaseType(p[1].typeList[0])
        if not helper.compareType(p[1].typeList[0], p[3].typeList[0]):
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Type should be same across binary operator')
        elif tp[0] not in p[2].extra:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Invalid type for binary expression')
        else:
            if len(p[2].typeList) > 0:
                # for boolean
                p[0].typeList = p[2].typeList
            else:
                p[0].typeList = p[1].typeList
            newVar = helper.newVar(p[0].typeList[0])
            p[0].code = p[1].code
            p[0].scopeInfo = p[1].scopeInfo
            p[0].code += p[3].code
            p[0].scopeInfo += p[3].scopeInfo
            if len(p[2].extra) < 3:
                p[0].code.append([p[2].extra['opcode'], newVar, p[1].placeList[0], p[3].placeList[0]])
                p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[1].placeList[0]), helper.findScope(p[3].placeList[0])])
            else:
                baseType = helper.getBaseType(p[1].typeList[0])
                p[0].code.append([p[2].extra['opcode'] + baseType[0], newVar, p[1].placeList[0], p[3].placeList[0]])
                p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[1].placeList[0]), helper.findScope(p[3].placeList[0])])
            p[0].placeList.append(newVar)
            p[0].extra['scope'] = helper.getScope()

def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                             | UnaryOp UnaryExpr
                             | NOT UnaryExpr'''
    p[0] = Node('UnaryExpr')
    p[0].extra['deref'] = ['no']
    if len(p) == 2:
        p[0].typeList = p[1].typeList
        p[0].placeList = p[1].placeList
        p[0].code = p[1].code
        p[0].scopeInfo = p[1].scopeInfo

    elif p[1] == '!':
        tp = helper.getBaseType(p[2].typeList[0])
        if tp != ['bool']:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Type should be boolean')
        else:
            p[0].typeList = p[2].typeList
            p[0].placeList = p[2].placeList
            p[0].code = p[2].code
            p[0].scopeInfo = p[2].scopeInfo
            newVar = helper.newVar(p[0].typeList[0])
            p[0].code.append(['!', newVar, p[2].placeList[0]])
            p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[2].placeList[0])])
    else:
        updateNeeded = True
        ck = False
        if p[1].extra['opcode'] == '*':
            ck = True
            rawType = helper.getBaseType(p[2].typeList[0])
            if rawType[0] != 'pointer':
                compilation_errors.add('TypeMismatch', line_number.get()+1, 'Expected pointer type')
            else:
                newType = helper.addUnNamedType(rawType[1])
                p[0].typeList = [newType]
                updateNeeded = False
        if p[1].extra['opcode'] == '&':
            ck = True
            rawType = helper.getBaseType(p[2].typeList[0])
            newType = helper.addUnNamedType(['pointer', rawType])
            p[0].typeList = [newType]
            updateNeeded = False
        rawType = helper.getBaseType(p[2].typeList[0])
        if rawType[0] not in p[1].extra and not ck:
            compilation_errors.add('TypeMismatch', line_number.get()+1, 'Invalid type for unary expression')
        else:
            if updateNeeded:
                p[0].typeList = p[2].typeList
                p[0].extra['deref'] = ['no']
            else:
                p[0].extra['deref'] = [p[1].extra['opcode'] + p[2].placeList[0]]
            newVar = helper.newVar(p[0].typeList[0])
            p[0].placeList = [newVar]
            p[0].identList = [newVar]
            p[0].code = p[2].code
            p[0].scopeInfo = p[2].scopeInfo
            p[0].code.append([p[1].extra['opcode'] + helper.getBaseType(p[2].typeList[0])[0], newVar, p[2].placeList[0]])
            p[0].scopeInfo.append(['',helper.getScope(),helper.findScope(p[2].placeList[0])])

def p_binary_op(p):
    '''BinaryOp : LOR
                            | LAND
                            | RelOp
                            | AddMulOp'''

    if isinstance(p[1], str):
        p[0] = Node('BinaryOp')
        p[0].extra['opcode'] = p[1]
        p[0].extra['bool'] = True
        p[0].typeList.append('bool')
    elif p[1].name == 'RelOp':
        p[0] = p[1]
        p[0].typeList.append('bool')
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
        # p[0].extra['string'] = True


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
    if p[1] == '+':
        p[0].extra['string'] = True
    p[0].extra['opcode'] = p[1]

# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
    '''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
    p[0] = p[4]
    p[0].name = 'Conversion'
    if (p[2].typeList[0][0] not in ['f', 'i']) or (p[4].typeList[0][0] not in ['i', 'f']):
        compilation_errors.add('TypeError', line_number.get()+1, 'Type conversion between only float/int allowed')
        return

    newVar = helper.newVar(p[2].typeList[0])
    p[0].code.append(['=', newVar, '(' + str(p[2].typeList[0]) + ')' + str(p[4].placeList[0])])
    p[0].scopeInfo.append(['', helper.getScope(), helper.findScope(p[4].placeList[0])])
    p[0].placeList = [newVar]
    p[0].typeList = p[2].typeList

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
                             | ForStmt
                             | PrintStmt
                             | ScanStmt'''
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
    rawType = helper.getBaseType(p[1].typeList[0])
    if  rawType[0] != 'int':
        err_ = str(p[1].typeList[0]) + 'cannot be incremented/decremented'
        compilation_errors.add('TypeMismatch', line_number.get()+1, err_)
    p[0].code.append([p[2], p[1].placeList[0], p[1].placeList[0]])
    p[0].scopeInfo.append(['', helper.findScope(p[1].placeList[0]), helper.findScope(p[1].placeList[0])])

def p_assignment(p):
    ''' Assignment : ExpressionList assign_op ExpressionList'''
    p[0] = p[1]
    if len(p[1].typeList) != len(p[3].typeList):
        err_ = str(len(p[1].typeList)) + ' identifier on left, while ' + str(len(p[3].placeList)) + ' expression on right'
        compilation_errors.add('Assignment Mismatch', line_number.get()+1, err_)
    else:
        for idx in range(len(p[3].typeList)):
            rawTp1 = helper.getBaseType(p[1].typeList[idx])
            rawTp2 = helper.getBaseType(p[3].typeList[idx])
            if not helper.compareType(rawTp1, rawTp2):
                err_ = str(rawTp1) + ' assigned to ' + str(rawTp2)
                compilation_errors.add('TypeMismatch', line_number.get()+1, err_)
            info = helper.findInfo(p[1].placeList[idx])
            if info is None:
                info = []
            if 'is_const' in info:
                compilation_errors.add('ConstantAssignment', line_number.get()+1, 'Constant cannot be reassigned')
            if p[2].extra['opcode'] != '=' and rawTp1[0] not in p[2].extra:
                compilation_errors.add('TypeMismatch', line_number.get()+1, 'Invalid Type for operator %s'%p[2].extra['opcode'])
    p[0].name = 'Assignment'
    p[0].code += p[3].code
    p[0].scopeInfo += p[3].scopeInfo
    for idx_ in range(len(p[3].typeList)):
        if p[1].extra['deref'][idx_] == 'no':
            p[0].code.append([p[2].extra['opcode'], p[1].placeList[idx_], p[3].placeList[idx_]])
        else:
            p[0].code.append([p[2].extra['opcode'], p[1].extra['deref'][idx_], p[3].placeList[idx_]])
        p[0].scopeInfo.append(['', helper.findScope(p[1].placeList[idx_]), helper.findScope(p[3].placeList[idx_])])

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
    rawType = helper.getBaseType(p[3].typeList[0])
    if rawType[0] != 'bool':
        compilation_errors.add('TypeError',line_number.get()+1, 'Non-bool expression (%s) used as if condition'%p[3].typeList[0])
    # if x relopy gotoL

    newLabel1 = helper.newLabel()
    p[0].code.append(['if',p[3].placeList[0],'==','False', 'goto',newLabel1])
    # Use extra information to get scope of expr because Last scope has been popped
    p[0].scopeInfo.append(['', p[3].extra['scope'], '', '', '', ''])
    p[0].code += p[4].code
    p[0].scopeInfo += p[4].scopeInfo
    newLabel2 = helper.newLabel()
    p[0].code.append(['goto', newLabel2])
    p[0].scopeInfo.append(['',''])
    p[0].code.append([newLabel1])
    p[0].scopeInfo.append([''])
    p[0].code += p[5].code
    p[0].scopeInfo += p[5].scopeInfo
    p[0].code.append([newLabel2])
    p[0].scopeInfo.append([''])

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

# --------------- IO STATEMENTS ----------------------------------

def p_print(p):
    '''PrintStmt : PRINT ExpressionList'''
    p[0] = p[2]
    p[0].name = 'PrintStmt'
    for idx, var in enumerate(p[2].placeList):
        p[0].code.append(['print_' + str(helper.getBaseType(p[2].typeList[idx])[0]), var])
        p[0].scopeInfo.append(['', helper.findScope(var)])

def p_scan(p):
    '''ScanStmt : SCAN ExpressionList'''
    p[0] = p[2]
    p[0].name = 'ScanStmt'
    for idx, var in enumerate(p[2].placeList):
        p[0].code.append(['scan_' + str(helper.getBaseType(p[2].typeList[idx])[0]), var])
        p[0].scopeInfo.append(['', helper.findScope(var)])

# -----------------------------------------------------------


# --------- FOR STATEMENTS AND OTHERS ---------------
def p_for(p):
    '''ForStmt : FOR CreateScope ConditionBlockOpt Block EndScope'''
    p[0] = p[3]
    start = helper.symbolTables[helper.lastScope].metadata['start']
    update = helper.symbolTables[helper.lastScope].metadata['update']
    end = helper.symbolTables[helper.lastScope].metadata['end']
    p[0].code += [[start]]
    p[0].scopeInfo.append([''])
    p[0].code += p[4].code
    p[0].scopeInfo += p[4].scopeInfo
    p[0].code += [['goto', update]]
    p[0].scopeInfo.append(['', ''])
    p[0].code += [[end]]
    p[0].scopeInfo.append([''])
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
        p[0].scopeInfo.insert(0, [''])
    if p[1].name == 'epsilon':
        p[0].extra['isInfinite'] = True
        p[0].code += [[update]]
        p[0].scopeInfo.append([''])
    p[0].name = 'ConditionBlockOpt'


def p_condition(p):
    '''Condition : Expression'''
    p[0] = p[1]
    end = helper.symbolTables[helper.getScope()].metadata['end']
    p[0].code.append(['if', p[1].placeList[0], '==', 'False', 'goto', end])
    p[0].scopeInfo.append(['', helper.findScope(p[1].placeList[0]), '', '', '',''])
    rawType = helper.getBaseType(p[1].typeList[0])
    if rawType[0] != 'bool':
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
    p[0].scopeInfo.append([''])
    p[0].code += p[3].code
    p[0].scopeInfo += p[3].scopeInfo
    p[0].code += [['goto', start]]
    p[0].scopeInfo.append(['', ''])
    p[0].code += [[update]]
    p[0].scopeInfo.append([''])
    p[0].code += p[5].code
    p[0].scopeInfo += p[5].scopeInfo
    p[0].code += [['goto', condition]]
    p[0].scopeInfo.append(['',''])
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

    scope_ = helper.getNearest('func')
    if scope_ == -1:
        compilation_errors.add('Scope Error', line_number.get()+1, 'return is not in a function')
        return

    typeList = helper.getRetType(scope_)
    if len(typeList) != len(p[2].typeList):
        error_ = 'Expected ' + str(len(typeList)) + ' arguments got ' + str(len(p[2].typeList))
        compilation_errors.add('Type Mismatch', line_number.get()+1,error_)
    elif len(typeList) != 0 and not helper.compareType(p[2].typeList[0], typeList[0]):
        compilation_errors.add('Type Error',line_number.get()+1, 'return type does not match')
    elif len(p[2].placeList) != 0:
        helper.updateRetVal(p[2].placeList[0])
        p[0].code = p[2].code + [['return', p[2].placeList[0]]]
        p[0].scopeInfo = p[2].scopeInfo + [['', helper.findScope(p[2].placeList[0])]]
    else:
        p[0].code = p[2].code + [['return']]
        p[0].scopeInfo = p[2].scopeInfo + [['']]

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
    p[0].scopeInfo = [['', '']]

def p_continue(p):
    '''ContinueStmt : CONTINUE'''
    p[0] = Node('ContinueStmt')
    scope_ = helper.getNearest('for')
    if scope_ == -1:
        compilation_errors.add('Scope Error', line_number.get()+1, 'continue is not in a loop')
        return
    symTab = helper.symbolTables[scope_]
    p[0].code = [['goto', symTab.metadata['update']]]
    p[0].scopeInfo = [['', '']]

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
        p[0].scopeInfo += p[2].scopeInfo


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
        return '    ' + codeList[0] + ' ' + codeList[1]
    elif len_ == 3:
        op = codeList[0]
        if op == '=':
            operand_ = codeList[2]
            if codeList[2][0] in ['&', '*']:
                operand_ = codeList[2][0] + '(' + codeList[2][1:] + ')'
            return '    ' + codeList[1] + ' = ' + operand_
        elif len(op) == 1:
            return '    ' + codeList[1] + ' = ' + op + '(' + codeList[2] + ')'
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
            rawTp = helper.getBaseType(type_[idx_])
            row = [key,rawTp,size_[idx_],offset_[idx_],is_const[idx_]]
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
    print("===== 3AC ====")
    assert(len(rootNode.code)==len(rootNode.scopeInfo))
    for idx in range(len(rootNode.code)):
        print("-------------------------")
        print(rootNode.code[idx])
        print(rootNode.scopeInfo[idx])

if compilation_errors.size() > 0:
    sys.exit()
generateCSV(csv_file)

for idx_ in range(len(rootNode.code)):
    code_file.write(getCodeString(rootNode.code[idx_]))
    code_file.write('\n')

code_file.close()
in_file.close()

import pickle as pkl
pkl.dump(rootNode, open('rootNode.p', 'wb'))
pkl.dump(helper, open('helper.p', 'wb'))
