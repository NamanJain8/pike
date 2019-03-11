
class Errors:
    def __init__(self):
        self.types = ['KeyError']
        self.error = []
        self.counter = 0
    
    def add(self,type_,lineno,string):
        self.counter += 1
        error = {}
        error["type"] = type_
        error["lineno"] = lineno
        error["msg"] = string
        (self.error).append(error)
        return error

    def printError(self, index):
        print(self.error[index])
        return

    def printErrors(self):
        for error in self.error:
            print(error)
        return

class symbolTable:

    def __init__(self):
        self.table = {}
        self.parent = None
        self.metadata = {}

    # Checks whether "id" lies in the symbol table
    def lookUp(self, id):
        return (id in self.table.keys())

    # Inserts if already not present
    def add(self, id, type_):
        if (not self.lookUp(id)):
            (self.table)[id] = {}
            (self.table)[id]["type"] = type_

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

class Node:
    def __init__(self,name):
        self.code = []
        self.typeList = []
        self.placeList = []
        self.identList = []
        self.name = name