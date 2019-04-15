import pickle as pkl
from data_structures import Helper, Node

asmCode = []

class CodeGenerator:
    def __init__(self, helper, rootNode):
        self.asmCode = []
        self.asmCode.append('.global main')
        self.asmCode.append('section .data')
        self.asmCode.append('print_int db "%i ", 0x00')
        self.asmCode.append('print_line db "", 0x0a, 0x00')
        self.dataIndex = 4
        self.codeIndex = 0
        self.asmCode.append('section .text')
        self.helper = helper
        self.scopeInfo = rootNode.scopeInfo
        self.code = rootNode.code


    def addFunc(self,name):
        funcScope = self.helper.symTables[0].functions[name]
        funcCode = []

        self.codeIndex += 1
        while True:
            curr = self.code[self.codeIndex]
            if len(curr) == 1 and curr[0][:-2] == '::':
                break
            funcCode.append(curr)
            self.codeIndex += 1

        # standard prologue
        self.add_prologue()

        # update stack pointer to store all the varaibles in current sym table
        self.asmCode.append('sub esp, '+str(helper.getWidth(funcScope)))

        # after every return statement call epilogue
        paramSize = # get from naman's code
        addrMap = {}

        # subtract the size of first param
        for x in self.helper.symTables[funcScope].table:
            if ('is_arg' in self.helper.symTables[funcScope].table[x]) and \
                self.helper.symTables[funcScope].table[x]['offset'] == 0:
                paramSize -= self.helper.symTables[funcScope].table[x]['size']
                break



        # get all the parameter values from stack


        # standard epilogue
        self.add_epilogue()


    def add_prologue(self, scope):
        self.asmCode.append('push ebp')
        self.asmCode.append('mov ebp, esp')

    def add_epilogue(self, scope):
        self.asmCode.append('mov esp, ebp')
        self.asmCode.append('pop ebp')
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
    helper = pkl.load(open('helper.p', 'rb'))

    # print(rootNode.scopeInfo)
    # Now can use helper class functions
    
    x86_code = CodeGenerator(helper, rootNode)

    for idx, instr in enumerate(rootNode.code):
        x86_code.genCode(instr, rootNode.scopeInfo[idx])

    outfile = open('assembly.asm', 'w')
    for code in x86_code.asmCode:
        outfile.write(code + '\n')