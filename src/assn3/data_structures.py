
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
        self.varCount = 0
        self.labelCount = 0
        self.scope = 0
        self.scopeStack = []
        self.offsetStack = []
        self.symbolTables = []

    def newVar(self):
        var = 't' + str(self.varCount)
        self.varCount += 1
        return var

    def newLabel(self):
        label = 'label' + str(self.labelCount)
        self.labelCount += 1
        return label

    def newOffset(self):
        self.offsetStack.append(0)
        return

    def getOffset(self):
        return self.offsetStack[-1]

    def popOffset(self):
        self.offsetStack.pop()

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
        self.scopeStack.pop()
        self.popOffset()

    def checkId(self,identifier, type_='default'):
        if type_ == 'global':
            if self.symbolTables[0].lookUp(identifier) is True:
                return True
            return False
        
        if type_ == "current":
            if self.symbolTables[self.getScope()].lookUp(identifier) is True:
                return True
            return False
        
        # wrong implemetation
        # if type_ == "label":
        #     if self.symbolTables[0].lookUp(identifier) is False:
        #         return True
        #     return False  
              
        # Couldnt figure *!s

        # Default case
        for scope in self.scopeStack[::-1]:
            if self.symbolTables[scope].lookUp(identifier) is True:
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
