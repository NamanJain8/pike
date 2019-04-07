
class Errors:
    def __init__(self):
        self.types = ['KeyError', 'Lexical Error']
        self.error = []
        self.counter = 0
    
    def add(self, type_, lineno, string):
        self.counter += 1
        err_ = {}
        err_["type"] = type_
        err_["lineno"] = lineno
        err_["msg"] = string
        # err_['colno'] = colno
        (self.error).append(err_)
        self.printError(self.counter-1)
        return

    def printError(self, index):
        err_ = self.error[index]
        error_string = '[' + err_['type'] + ']: ' + err_['msg'] + ' (line: ' + str(err_['lineno'])
        # if err_['colno'] != None:
        #     error_string += ', column no: ' + str(err_['colno'])
        error_string += ')'
        print(error_string)
        return

    def printErrors(self):
        for idx in range(len(self.error)):
            self.printError(idx)
        return

    def size(self):
        return len(self.error)



class SymbolTable:
    
    def __init__(self, parent=None):
        self.typeDefs = {} # this is a dictionary of dictionary, in which each type name is key
                           # for each key, all the declarations are key in the new dict, with type, size tuple
                           # In this dictionary we will also store the total size
        self.functions = {} # we  need to store index of its symbol table, and the label from which code starts
        self.table = {}
        self.parent = parent
        self.metadata = {}
        self.metadata['name'] = 'global'

        # metadata has a key 'is_function' to check if the current symbol table is activation record.

    def __str__(self):
        print('\n')
        print('typeDefs:',self.typeDefs)
        print('functions:',self.functions)
        print('parent:', self.parent)
        print('table:', self.table)
        print('metadata', self.metadata)
        return ""

    # Checks whether "id" lies in the symbol table
    def lookUp(self, id):
        return (id in self.table.keys())
    
    def lookUpType(self,id):
        return (id in self.typeDefs.keys())

    # Inserts if already not present
    def add(self, id, type_):
        if (not self.lookUp(id)):
            (self.table)[id] = {}
            (self.table)[id]['type'] = type_

    # Returns the argument list of the variable else returns None
    # Note that type is always a key in argument list
    def get(self, id):
        if(self.lookUp(id)):
            return (self.table)[id]

        return None

    # Updates the variable of id id with arg list of KEY key with VALUE value
    def update(self, id, key, value):
        try:
            (self.table)[id][key] = value
            return True
        except KeyError:
            return False


    def setParent(self, parent):
        self.parent = parent

    def updateMetadata(self,key,value):
        self.metadata[key]=value

class Helper:
    def __init__(self):
        # everything in type list is in compact form, ie they are strings.
        self.varCount = 0
        self.labelCount = 0
        self.scope = 0
        self.scopeStack = []
        self.offsetStack = [0]
        self.symbolTables = []
        self.lastScope = 0
        self.typeincr = 0
        self.type = {}
        self.type['int'] = {'size': 4, 'type': ['int']}
        self.type['bool'] = {'size': 1, 'type': ['bool']}
        self.type['string'] = {'size': 4, 'type': ['string']}
        self.type['float'] = {'size': 8, 'type': ['float']}
        # for structure type would be like 'type': ['struct', {'a': {'size': 4, 'type': ['int'], offset: 4}}]
        # array would be like type['arr'] = {type: ['array', {'type': expanded form, 'len': 10}, 'size': }
        # slices like type['slice'] = {type: ['slice', {'type': expanded form, 'len': 10}], size}

    def getSize(self, type_):
        # returns the size for the given type by indexing it in type map.
        return self.type[type_]['size']

    def getBaseType(self, type_):
        # returns the expanded form of type
        return self.type[type_]['type']

    def computeSize(self, type_):
        # computes size for a expanded type
        if type_[0] == 'pointer':
            return 4
        elif type_[0] == 'struct':
            sz = 0
            for key in type_[1]:
                # enumerate the struct dictionary.
                sz += self.computeSize(type_[1][key]['type'])
            return sz
        elif type_[0] == 'array' or type_[0] == 'slice':
            sz = self.computeSize(type_[1]['type'])
            return (type_[1]['len'] * sz)
        else:
            # it must be a base type then.
            return self.type[type_[0]]['size']

    def addUnNamedType(self, type_):
        r'''
        Input: type in expanded form
        this function adds this new type in type dictionary.
        This might be useful when the type does not have a explicit name.
        '''
        typeName = 'type' + str(self.typeincr)
        self.typeincr += 1
        sz = self.computeSize(type_)
        self.type[typeName] = {'size': sz, 'type': type_}
        return typeName

    def newVar(self, type_):
        # this type_ should be in compact form, ie. a string name.
        var = 't' + str(self.varCount)
        self.symbolTables[self.getScope()].add(var, type_)
        size_ = self.getSize(type_)
        self.symbolTables[self.getScope()].update(var, 'size', size_)
        self.symbolTables[self.getScope()].update(var, 'offset', self.getOffset())
        self.updateOffset(size_)
        self.varCount += 1
        return var

    def newLabel(self):
        if (self.labelCount == 0): # just to make 3AC pretty!
            label = 'Program Start'
        else:
            label = 'label' + str(self.labelCount)
        self.labelCount += 1
        return label

    def newOffset(self):
        self.offsetStack.append(self.getOffset())
        return

    def getOffset(self):
        return self.offsetStack[-1]

    def popOffset(self):
        return self.offsetStack.pop()

    def updateOffset(self, size):
        self.offsetStack[-1] += size

    def newScope(self, parent=None):
        newTable = SymbolTable(parent)
        newTable.updateMetadata('scopeNo', self.scope)
        self.symbolTables.append(newTable)
        self.scopeStack.append(self.scope)
        self.newOffset()
        self.scope += 1

    def getScope(self):
        return self.scopeStack[-1]

    def endScope(self):
        self.lastScope = self.scopeStack.pop()
        self.popOffset()

    def checkId(self,identifier, type_='default'):
        if identifier in self.symbolTables[0].functions.keys():
            return True
            
        if type_ == 'global':
            if self.symbolTables[0].lookUp(identifier) is True:
                return True
            return False
        
        if type_ == "current":
            if self.symbolTables[self.getScope()].lookUp(identifier) is True:
                return True
            return False

        # Default case
        for scope in self.scopeStack[::-1]:
            if self.symbolTables[scope].lookUp(identifier) is True:
                return True
        return False

    def checkType(self, identifier):
        if identifier in self.type:
            return True
        return False

    def findInfo(self, identifier, type_='default'):
        if type_ == 'global':
            if self.symbolTables[0].get(identifier) is not None:
                return self.symbolTables[0].get(identifier)
        
        else:
            for scope in self.scopeStack[::-1]:
                if self.symbolTables[scope].get(identifier) is not None:
                    return self.symbolTables[scope].get(identifier)

            for scope in self.scopeStack[::-1]:
                if self.symbolTables[scope].typeDefs.get(identifier) is not None:
                    return self.symbolTables[scope].typeDefs.get(identifier)
        return None

    def findScope(self, identifier):
        for scope in self.scopeStack[::-1]:
            if self.symbolTables[scope].get(identifier) is not None:
                return scope

    def getNearest(self, type_):
        # return nearest parent scope with name = type_(func, for), -1 if no such scope exist
        for scope in self.scopeStack[::-1]:
            if self.symbolTables[scope].metadata['name'] == type_:
                return scope
        return -1

    def addFunc(self, name):
        # add the name in the current(global for now :P) symbol table with its scope
        self.symbolTables[0].functions[name] = self.scope

    def makeSymTabFunc(self):
        # make the current symbol table as a function symbol table
        self.symbolTables[self.getScope()].metadata['is_function'] = 1

    def updateSignature(self, typeList):
        # update the signature in function symbol table
        # signature is stored as a list of argument types
        scope_ = self.getNearest('func')
        assert(self.symbolTables[scope_].metadata['is_function'] == 1)
        self.symbolTables[scope_].metadata['num_arg'] = len(typeList)
        self.symbolTables[scope_].metadata['signature'] = typeList

    def updateRetValType(self, retvaltp):
        # needed when we do checking inside the function body, on return statement.
        # set the variable which stores the return value type in the symbol table of current scope
        scope_ = self.getNearest('func')
        assert(self.symbolTables[scope_].metadata['is_function'] == 1)
        self.symbolTables[scope_].metadata['retvaltype'] = retvaltp

    def updateRetVal(self, retval):
        # needed when we want to find the place holder of return value.
        # set the variable which stores the return value in the symbol table of current scope
        scope_ = self.getNearest('func')
        assert(self.symbolTables[scope_].metadata['is_function'] == 1)
        self.symbolTables[scope_].metadata['retval'] = retval

    def getRetType(self, scope):
        # returns the return type of a function provided the scope number of that function
        funcMeta = self.symbolTables[scope].metadata
        return funcMeta['retvaltype']

    def updateSize(self,sizeList):
        # update the signature in function symbol table
        # signature is stored as a list of argument size
        scope_ = self.getNearest('func')
        assert(self.symbolTables[scope_].metadata['is_function'] == 1)
        self.symbolTables[scope_].metadata['retvalsize'] = sizeList
    
    def getRetSize(self,scope):
        # returns the return size of a function provided the scope number of that function
        funcMeta = self.symbolTables[scope].metadata
        return funcMeta['retvalsize']

    def lookUpfunc(self, name):
        # checks if the function is defined in the global scope, and returns its scope
        # if it is not defined it returns -1
        if name in self.symbolTables[0].functions.keys():
            return self.symbolTables[0].functions[name]
        else:
            return -1

    def compareType(self, tp1, tp2):
        # given 2 types (in compact form), checks wheather they denote same type or not
        if tp1 == tp2:
            return True
        elif self.getBaseType(tp1) == self.getBaseType(tp2):
            return True
        else:
            return False

    def checkArguments(self, name, arguments):
        # checks for a given function name and argument type list, matches with the function signature
        # returns 'cool' if no error found
        funcScope = self.lookUpfunc(name)
        if funcScope == -1:
            return 'function ' + name + ' not declared'
        
        funcMeta = self.symbolTables[funcScope].metadata
        if len(arguments) != funcMeta['num_arg']:
            return 'number of arguments do not match the function signature'
        
        for i in range(len(arguments)):
            expectedTp = funcMeta['signature'][i]
            if not self.compareType(arguments[i], expectedTp):
                return 'Argument ' + str(i+1) + ' is expected to be ' + str(self.getBaseType(expectedTp)) + \
                        ' but given ' + str(self.getBaseType(arguments[i]))
    
        return 'cool'

    def debug(self):
        print('varCount:',self.varCount)
        print('lebelCount:',self.labelCount)
        print('scope:',self.scope)
        print('scopeStack:',self.scopeStack)
        print('offsetStack:',self.offsetStack)
        for table in range(len(self.symbolTables)):
            print('symbolTable %d:'%table,self.symbolTables[table])


class Node:
    def __init__(self,name):
        self.code = []
        self.typeList = []
        self.placeList = []
        self.identList = []
        self.name = name
        self.sizeList = []
        self.extra = {}

class LineCount:
    def __init__(self):
        self.lineno = 0

    def add(self, count):
        self.lineno += count

    def get(self):
        return self.lineno
