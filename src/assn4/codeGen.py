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

    def add_op(self, instr, scopeInfo, funcScope):
        # load into registers

        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp +' + str(src1Offset) + ']')
        code.append('mov esi, [ebp +' + str(src2Offset) + ']')
        code.append('add edi, esi')
        code.append('mov [ebp + ' + str(dstOffset) + '], edi')
        return code
    
    def mul_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp +' + str(src1Offset) + ']')
        code.append('mov esi, [ebp +' + str(src2Offset) + ']')
        code.append('imul edi, esi')
        code.append('mov [ebp + ' + str(dstOffset) + '], edi')
        return code
    
    def assign_op(self, instr, scopeInfo, funcScope):
        # load into registers

        dst = instr[1]
        src = instr[2]
        code = []

        if isinstance(scopeInfo[2], int):
            dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
            srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)
            code.append('mov edi, [ebp' + srcOffset + ']')
            code.append('mov [ebp' + dstOffset + '], edi')
        else:
            dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
            code.append('mov esi, ' + str(src1))
            code.append('mov [ebp' + dstOffset + '], edi')
        return code

    def genCode(self, idx, funcScope):
        # Check instruction type and call function accordingly
        instr = self.code[idx]
        scopeInfo = self.scopeInfo[idx]

        if instr[0] == 'return':
            return []
        if len(instr) == 1:
            return [instr[0]+':']
        if instr[0] == '+int':
            return self.add_op(instr, scopeInfo, funcScope)
        if instr[0] == '*int':
            return self.mul_op(instr, scopeInfo, funcScope)
        if instr[0] == '=':
            return self.assign_op(instr, scopeInfo, funcScope)
        
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