import pickle as pkl
from data_structures import Helper, Node

class CodeGenerator:
    def __init__(self):
        self.asmCode = []
        self.asmCode.append('section .text')
        self.asmCode.append('   .global _start')

    def add_prologue(self, scope):
        self.asmCode.append('push %esp')
        self.asmCode.append('mov %esp, %ebp')
        self.asmCode.append('sub $' + str(100) + ', %esp')
        self.asmCode.append('push %edi')
        self.asmCode.append('push %esi')

    def add_epilogue(self, scope):
        self.asmCode.append('pop %esi')
        self.asmCode.append('pop %edi')
        self.asmCode.append('mov %ebp, %esp')
        self.asmCode.append('pop %ebp')
        self.asmCode.append('ret')

    def add_op(self, dst, src1, src2, dstScope, src1Scope, src2Scope):
        # load into registers
        src1Offset = helper.symTables[int(src1Scope)].get(src1)['offset']
        src2Offset = helper.symTables[int(src2Scope)].get(src2)['offset']
        dstOffset = helper.symTables[int(dstScope)].get(dst)['offset']
        self.asmCode.append('mov -' + str(src1Offset) + '(%ebp), %eax')
        self.asmCode.append('mov -' + str(src2Offset) + '(%ebp), %ebx')
        self.asmCode.append('add %ebx, %ebx')
        self.asmCode.append('mov %eax, -' + str(dstOffset) + '(%ebp)')
        
    
    def mul_op(self, dst, src1, src2, dstScope, src1Scope, src2Scope):
        # load into registers
        src1Offset = helper.symTables[src1Scope].get(src1)['offset']
        print(src1Offset)
    
    def assign_op(self, dst, src1, dstScope, src1Scope):
        # load into registers
        if isinstance(src1Scope, int):
            src1Offset = helper.symTables[int(src1Scope)].get(src1)['offset']
            dstOffset = helper.symTables[int(dstScope)].get(dst)['offset']
            self.asmCode.append('mov -' + str(src1Offset) + '(%ebp), %eax')
            self.asmCode.append('mov %eax, -' + str(dstOffset) + '(%ebp)')
        else:
            dstOffset = helper.symTables[int(dstScope)].get(dst)['offset']
            self.asmCode.append('mov $' + str(src1) + ', %eax')
            self.asmCode.append('mov %eax, -' + str(dstOffset) + '(%ebp)')
    

    def genCode(self, instr, scopeInfo):
        # Check instruction type and call function accordingly
        # If label and is function:
        if instr[0][:4] == 'main':
            # pass scope of function
            self.add_prologue(1)
        if instr[0] == 'return':
            self.add_epilogue(1)
        if instr[0] == '+i':
            self.add_op(instr[1], instr[2], instr[3], scopeInfo[1], scopeInfo[2], scopeInfo[3])
        if instr[0] == '*':
            self.mul_op(instr[1], instr[2], instr[3], scopeInfo[1], scopeInfo[2], scopeInfo[3])
        if instr[0] == '=':
            self.assign_op(instr[1], instr[2], scopeInfo[1], scopeInfo[2])
        
if __name__=='__main__':
    # Load files
    rootNode = pkl.load(open('rootNode.p', 'rb'))
    assert(len(rootNode.code) == len(rootNode.scopeInfo))
    symTables = pkl.load(open('symTables.p', 'rb'))

    print(rootNode.scopeInfo)
    # Now can use helper class functions
    helper = Helper()
    helper.symTables = symTables
    
    x86_code = CodeGenerator()

    for idx, instr in enumerate(rootNode.code):
        x86_code.genCode(instr, rootNode.scopeInfo[idx])

    outfile = open('assembly.s', 'w')
    for code in x86_code.asmCode:
        outfile.write(code + '\n')