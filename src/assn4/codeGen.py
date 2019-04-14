import pickle as pkl
from data_structures import Helper, Node

class CodeGenerator:
    def __init__(self):
        self.asmCode = []
        self.asmCode.append('.text')
        self.asmCode.append('.globl myfunc')
        self.asmCode.append('.type myfunc, @function')
        self.asmCode.append('myfunc:')

    def genCode(self, instr, scopeInfo):
        # Check instruction type and call function accordingly
        a = 1

if __name__=='__main__':
    # Load files
    rootNode = pkl.load(open('rootNode.p', 'rb'))
    assert(len(rootNode.code) == len(rootNode.scopeInfo))
    symTables = pkl.load(open('symTables.p', 'rb'))

    # Now can use helper class functions
    helper = Helper()
    helper.symTables = symTables
    
    x86_code = CodeGenerator()

    for idx, instr in enumerate(rootNode.code):
        x86_code.genCode(instr, rootNode.scopeInfo[idx])

    for code in x86_code.asmCode:
        print(code)