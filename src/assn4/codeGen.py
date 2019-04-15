import pickle as pkl
from data_structures import Helper, Node

asmCode = []

class CodeGenerator:
    def __init__(self, helper, rootNode):
        self.asmCode = []
        self.asmCode.append('global main')
        self.asmCode.append('extern printf')
        self.asmCode.append('extern scanf')
        self.asmCode.append('section .data')
        self.asmCode.append('print_int db "%i ", 0x00')
        self.asmCode.append('print_line db "", 0x0a, 0x00')
        self.asmCode.append('scan_int db "%d", 0')
        self.dataIndex = 7
        self.codeIndex = 0
        self.asmCode.append('section .text')
        self.helper = helper
        self.scopeInfo = rootNode.scopeInfo
        self.code = rootNode.code

    def ebpOffset(self, ident, identScope, funcScope):
        paramSize = helper.getParamWidth(funcScope)
        paramSizeCopy = paramSize

        # subtract the size of first param
        for x in self.helper.symbolTables[funcScope].table:
            if ('is_arg' in self.helper.symbolTables[funcScope].table[x]) and \
                self.helper.symbolTables[funcScope].table[x]['offset'] == 0:
                paramSize -= self.helper.symbolTables[funcScope].table[x]['size']
                break

        offset = 0
        if 'is_arg' in self.helper.symbolTables[funcScope].table[ident]:
            offset = 8 + paramSize - self.helper.symbolTables[funcScope].table[ident]['offset']
        else:
            offset = -(self.helper.symbolTables[funcScope].table[ident]['offset'] - paramSizeCopy)
        if offset >= 0:
            return '+'+str(offset)
        return str(offset)
            
    def addFunc(self,name):
        funcScope = self.helper.symbolTables[0].functions[name]
        
        # add function label
        self.asmCode.append(name+':')

        # standard prologue
        self.add_prologue()

        # update stack pointer to store all the varaibles(except parameters) in current sym table
        self.asmCode.append('sub esp, '+str(helper.getParamWidth(funcScope)))

        self.codeIndex += 1
        while True:
            if self.codeIndex >= len(self.code):
                break
            curr = self.code[self.codeIndex]
            if (len(curr) == 1 and curr[0][-2:] == '::'):
                break
            code_ = self.genCode(self.codeIndex, funcScope)
            if len(code_) == 0:
                # then it should be a return statement
                if len(self.code[self.codeIndex] != 1):
                    # this represents a non void function hence return value needs to be updated in eax
                    retValOffset = self.ebpOffset(self.code[self.codeIndex][1])
                    self.asmCode.append('lea eax, [ebp'+str(retValOffset) + ']')
                self.add_epilogue()
            else:
                self.asmCode += code_
            self.codeIndex += 1

        # standard epilogue
        self.add_epilogue()


    def add_prologue(self):
        self.asmCode.append('push ebp')
        self.asmCode.append('mov ebp, esp')

    def add_epilogue(self):
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
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        code.append('add edi, esi')
        code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code
    
    def mul_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        code.append('imul edi, esi')
        code.append('mov [ebp' + str(dstOffset) + '], edi')
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
            code.append('mov edi, ' + str(src))
            code.append('mov [ebp' + dstOffset + '], edi')
        return code

    def print_int(self, instr, scopeInfo, funcScope):
        src = instr[1]
        srcOffset = self.ebpOffset(src, scopeInfo[1], funcScope)
        code = []
        code.append('mov esi, [ebp' + srcOffset + ']')
        code.append('push esi')
        code.append('push print_int')
        code.append('call printf')
        code.append('pop esi')
        code.append('pop esi')
        return code

    def scan_int(self, instr, scopeInfo, funcScope):
        src = instr[1]
        srcOffset = self.ebpOffset(src, scopeInfo[1], funcScope)
        code = []
        code.append('lea esi, [ebp' + srcOffset + ']')
        code.append('push esi')
        code.append('push scan_int')
        code.append('call scanf')
        code.append('pop esi')
        code.append('pop esi')
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
        if instr[0] == 'print_int':
            return self.print_int(instr, scopeInfo, funcScope)
        if instr[0] == 'scan_int':
            return self.scan_int(instr, scopeInfo, funcScope)

    def getCode(self):
        while True:
            if self.codeIndex >= len(self.code):
                break
            funcName = self.code[self.codeIndex][0].split(':')
            self.addFunc(funcName[0])
        return self.asmCode

if __name__=='__main__':
    # Load files
    rootNode = pkl.load(open('rootNode.p', 'rb'))
    assert(len(rootNode.code) == len(rootNode.scopeInfo))
    helper = pkl.load(open('helper.p', 'rb'))

    # print(rootNode.scopeInfo)
    # Now can use helper class functions
    
    codeGen = CodeGenerator(helper, rootNode)

    outfile = open('assembly.asm', 'w')
    x86Code = codeGen.getCode()

    for code_ in x86Code:
        if code_.split(' ')[0] in ['global', 'section', 'extern']:
            outfile.write(code_ + '\n')
        elif code_[-1:] == ':' and code_[0] == 'm':
            outfile.write('main:\n')
        elif code_[-1:] == ':':
            outfile.write(code_ + '\n')
        else:
            outfile.write('    '+code_+'\n')
    outfile.close()
