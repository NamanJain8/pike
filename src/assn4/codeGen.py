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
        self.asmCode.append('print_float db "%f ", 0x00')
        self.asmCode.append('print_line db "", 0x0a, 0x00')
        self.asmCode.append('scan_int db "%d", 0')
        self.dataIndex = 8
        self.codeIndex = 0
        self.asmCode.append('section .text')
        self.helper = helper
        self.counter = 0
        self.scopeInfo = rootNode.scopeInfo
        self.code = rootNode.code
        self.relops = ['==int', '!=int', '<=int', '>=int', '>int', '<int']

    def ebpOffset(self, ident, identScope, funcScope):
        paramSize = helper.getParamWidth(funcScope)

        offset = 0
        if 'is_arg' in self.helper.symbolTables[identScope].table[ident]:
            if 'parent' not in self.helper.symbolTables[identScope].table[ident]:
                offset = 8 + paramSize - self.helper.symbolTables[identScope].table[ident]['size'] - self.helper.symbolTables[identScope].table[ident]['offset']
            else:
                offset = 8 + paramSize - self.helper.symbolTables[identScope].table[ident]['offset']
                
        else:
            if 'parent' in self.helper.symbolTables[identScope].table[ident]:
                # parent = self.helper.symbolTables[identScope].table[ident]['parent']
                # parentScope = self.helper.symbolTables[identScope].table[ident]['parentScope']
                offset = -(self.helper.symbolTables[identScope].table[ident]['offset']  - paramSize)
            else:
                offset = -(self.helper.symbolTables[identScope].table[ident]['offset'] + self.helper.symbolTables[identScope].table[ident]['size'] - paramSize)
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
        self.asmCode.append('sub esp, '+str(helper.getWidth(funcScope) - helper.getParamWidth(funcScope) + helper.getLargest(funcScope)))

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
                if len(self.code[self.codeIndex]) != 1:
                    # this represents a non void function hence return value needs to be updated in eax
                    retValOffset = self.ebpOffset(self.code[self.codeIndex][1], self.scopeInfo[self.codeIndex][1], funcScope)
                    self.asmCode.append('lea eax, [ebp'+str(retValOffset) + ']')
                self.add_epilogue()
            else:
                if code_[0] != 'none':
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

    def unary_minus(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        code.append('mov esi, 0')
        code.append('sub esi, edi')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], esi')
        return code

    def setFlags(self, instr, scopeInfo):
        flag = [0 for x in instr]
        for i in range(1,len(instr)):
            try:
                if 'reference' in self.helper.symbolTables[scopeInfo[i]].get(instr[i]):
                    flag[i] = 1
            except:
                pass
        return flag

    def add_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.setFlags(instr, scopeInfo)

        info_src1 = self.helper.symbolTables[scopeInfo[2]].get(src1)

        baseType = helper.getBaseType(info_src1['type'])
        # TODO add the flag logic here as well
        if baseType[0] == 'struct':
            objOffset = int(self.ebpOffset(src1, scopeInfo[2], funcScope))
            self.helper.symbolTables[scopeInfo[1]].table[dst]['offset'] = -(objOffset + int(src2))
            self.helper.symbolTables[scopeInfo[1]].table[dst]['parent'] = src1
            # self.helper.symbolTables[scopeInfo[1]].table[dst]['parentScope'] = scopeInfo[2]
            return ['none']
        elif baseType[0] == 'array':
            objOffset = self.ebpOffset(src1, scopeInfo[2], funcScope)
            dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)
            return ['mov edx, '+str(objOffset),
                    'mov esi, [ebp'+str(src2Offset)+']',
                    'add edx, esi',
                    'mov esi, ebp',
                    'add esi, edx',
                    'mov [ebp' + str(dstOffset) + '], esi',
                ]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')

        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))

        code.append('add edi, esi')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def fadd_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('fld qword [ebp' + str(src1Offset) + ']')
        print(scopeInfo)
        if isinstance(scopeInfo[3], int):
            code.append('fld qword [ebp' + str(src2Offset) + ']')
        else:
            code.append('fld ' + str(src2))
        code.append('faddp')
        code.append('fstp qword [ebp' + str(dstOffset) + ']')
        return code

    def sub_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')

        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))
        code.append('sub edi, esi')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def fsub_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('fld qword [ebp' + str(src1Offset) + ']')
        print(scopeInfo)
        if isinstance(scopeInfo[3], int):
            code.append('fld qword [ebp' + str(src2Offset) + ']')
        else:
            code.append('fld ' + str(src2))
        code.append('fsubp')
        code.append('fstp qword [ebp' + str(dstOffset) + ']')
        return code

    def mul_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')

        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))
        code.append('imul edi, esi')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def fmul_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('fld qword [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            code.append('fld qword [ebp' + str(src2Offset) + ']')
        else:
            code.append('fld ' + str(src2))
        code.append('fmul qword [ebp' + str(src1Offset) + ']')
        code.append('fstp qword [ebp' + str(dstOffset) + ']')
        return code

    def div_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('xor edx, edx')
        code.append('mov eax, [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            code.append('mov ebi, [ebp' + str(src2Offset) + ']')
        else:
            code.append('mov ebx, ' + str(src2))
        code.append('idiv ebx')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], eax')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], eax')
        return code

    def pointer_assign(self, instr, scopeInfo, funcScope):
        dst = instr[1][1:]
        src = instr[2]
        code = []
        instr[1] = dst
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)

        code.append('mov edi, [ebp' + srcOffset + ']')
        if flag[2] == 1:
            code.append('mov edi [edi]')
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        code.append('mov [esi], edi')
        return code

    def assign_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src = instr[2]
        code = []
        flag = self.setFlags(instr, scopeInfo)

        if dst[0] == '*':
            return self.pointer_assign(instr, scopeInfo, funcScope)

        data_ = helper.symbolTables[scopeInfo[1]].get(instr[1])
        # if src is eax then we should assign the returned value
        # TODO add the flag logic here
        if src == 'eax':
            baseType = helper.getBaseType(data_['type'])
            offset = self.ebpOffset(instr[1], scopeInfo[1], funcScope)

            self.counter += 1
            label = 'looping' + str(self.counter)
            iters = int(data_['size'] / 4)
            code_ = ['mov esi, ebp']
            code_.append('add esi, '+offset)
            code_.append('mov cx, '+str(iters))
            code_.append(label + ':')
            code_.append('mov edx, [eax]')
            code_.append('mov [esi], edx')
            code_.append('add esi, 4')
            code_.append('add eax, 4')
            code_.append('dec cx')
            code_.append('jnz '+label)
            return code_

        if data_['type'] == 'float':
            if isinstance(scopeInfo[2], int):
                dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
                srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)
                code.append('fld qword [ebp' + srcOffset + ']')
                code.append('fstp qword [ebp' + dstOffset + ']')
            else:
                dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
                code.append('fld ' + str(src))
                code.append('fstp qword [ebp' + dstOffset + ']')
        else:
            if isinstance(scopeInfo[2], int):
                dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
                srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)
                code.append('mov edi, [ebp' + srcOffset + ']')
                if flag[2] == 1:
                    code.append('mov edi, [edi]')
                if flag[1] == 1:
                    code.append('mov esi, [ebp'+ str(dstOffset) + ']')
                    code.append('mov [esi], edi')
                else:
                    code.append('mov [ebp' + str(dstOffset) + '], edi')
            else:
                dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
                code.append('mov edi, ' + str(src))
                if flag[1] == 1:
                    code.append('mov esi, [ebp'+ str(dstOffset) + ']')
                    code.append('mov [esi], edi')
                else:
                    code.append('mov [ebp' + str(dstOffset) + '], edi')

        return code

    def assign_op_ptr(self, instr, scopeInfo, funcScope):
        dst = instr[1][1:]
        src = instr[2]
        # *t1 += t2
        code = []
        instr[1] = dst
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)
        code.append('mov edi, [ebp' + srcOffset + ']')
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if instr[0] == '+=':
            code.append('add [esi], edi')
        elif instr[0] == '-=':
            code.append('sub [esi], edi')
        elif instr[0] == '*=':
            code.append('imul edi, [esi]')
            code.append('mov [esi], edi')
        elif instr[0] == '/=':
            code.append('xor edx, edx')
            code.append('mov eax, [esi]')
            code.append('idiv edi')
            code.append('mov [esi], eax')
        return code

    def assign_ptr_rhs(self, instr, scopeInfo, funcScope):
        sz = helper.symbolTables[scopeInfo[1]].get(instr[1])['size']
        dst = instr[1]
        src = instr[2]
        code = []
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)

        ctr1 = 0
        ctr2 = 0
        while ctr2 < sz:
            var1 = ctr1 + int(dstOffset)
            if var1 >= 0:
                var1 = '+' + str(var1)
            code.append('mov esi, [ebp' + srcOffset + ']')
            if flag[2] == 1:
                code.append('mov esi, [esi]')
            code.append('sub esi,' + str(ctr2))
            code.append('mov edi, [esi]')
            if flag[1] == 1:
                code.append('mov esi, [ebp' + str(var1) +']')
                code.append('mov [esi], edi')
            else:
                code.append('mov [ebp' + str(var1) +'], edi')
            ctr1 += 4
            ctr2 += 4
        return code


    def add_assign_op(self, instr, scopeInfo, funcScope):
        if instr[1][0] == '*':
            return self.assign_op_ptr(instr, scopeInfo, funcScope)
        instr.insert(2,instr[1])
        scopeInfo.insert(2, scopeInfo[1])
        return self.add_op(instr, scopeInfo, funcScope)

    def sub_assign_op(self, instr, scopeInfo, funcScope):
        if instr[1][0] == '*':
            return self.assign_op_ptr(instr, scopeInfo, funcScope)
        instr.insert(2,instr[1])
        scopeInfo.insert(2, scopeInfo[1])
        return self.sub_op(instr, scopeInfo, funcScope)

    def mul_assign_op(self, instr, scopeInfo, funcScope):
        if instr[1][0] == '*':
            return self.assign_op_ptr(instr, scopeInfo, funcScope)
        instr.insert(2,instr[1])
        scopeInfo.insert(2, scopeInfo[1])
        return self.mul_op(instr, scopeInfo, funcScope)

    def div_assign_op(self, instr, scopeInfo, funcScope):
        if instr[1][0] == '*':
            return self.assign_op_ptr(instr, scopeInfo, funcScope)
        instr.insert(2,instr[1])
        scopeInfo.insert(2, scopeInfo[1])
        return self.div_op(instr, scopeInfo, funcScope)

    def ampersand_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src = instr[2]
        flag = self.setFlags(instr, scopeInfo)
        print(flag, instr)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        srcOffset = self.ebpOffset(src, scopeInfo[2], funcScope)
        code = []

        # if flag[2] == 1:
        #     code.append('mov edi, [ebp'+ srcOffset +']')
        # else:
        code.append('lea edi, [ebp'+ srcOffset +']')
        
        # if flag[2] == 1:
        #     code.append('mov esi, [ebp' + dstOffset + ']')
        #     code.append('mov [esi], edi')
        # else:
        code.append('mov [ebp'+dstOffset+'], edi')
        return code

    def relops_cmp(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        if flag[3] == 1:
            code.append('mov esi, [esi]')
        code.append('xor eax, eax')
        code.append('cmp edi, esi')
        if instr[0] == '==int':
            code.append('sete al')
        elif instr[0] == '!=int':
            code.append('setne al')
        elif instr[0] == '<int':
            code.append('setl al')
        elif instr[0] == '>int':
            code.append('setg al')
        elif instr[0] == '<=int':
            code.append('setle al')
        elif instr[0] == '>=int':
            code.append('setge al')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], eax')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], eax')
        return code

    def print_int(self, instr, scopeInfo, funcScope):
        src = instr[1]
        srcOffset = self.ebpOffset(src, scopeInfo[1], funcScope)
        flag = self.setFlags(instr, scopeInfo)
        code = []
        code.append('mov esi, [ebp' + srcOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        code.append('push esi')
        code.append('push print_int')
        code.append('call printf')
        code.append('pop esi')
        code.append('pop esi')
        return code

    def print_float(self, instr, scopeInfo, funcScope):
        src = instr[1]
        srcOffset = self.ebpOffset(src, scopeInfo[1], funcScope)
        code = []
        code.append('mov esi, [ebp' + srcOffset + ']')
        code.append('push esi')
        code.append('push print_float')
        code.append('call printf')
        code.append('pop esi')
        code.append('pop esi')
        return code

    def scan_int(self, instr, scopeInfo, funcScope):
        src = instr[1]
        flag = self.setFlags(instr, scopeInfo)
        srcOffset = self.ebpOffset(src, scopeInfo[1], funcScope)
        code = []
        code.append('lea esi, [ebp' + srcOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        code.append('push esi')
        code.append('push scan_int')
        code.append('call scanf')
        code.append('pop esi')
        code.append('pop esi')
        return code

    def param(self, instr, scopeInfo, funcScope):
        data_ = helper.symbolTables[scopeInfo[1]].get(instr[1])
        baseType = helper.getBaseType(data_['type'])
        offset = self.ebpOffset(instr[1], scopeInfo[1], funcScope)
        if baseType[0] in ['int', 'bool', 'float', 'string']:

            return ['mov edx, [ebp' + offset + ']', 'push edx']
        else:
            self.counter += 1
            label = 'looping' + str(self.counter)
            iters = int(data_['size'] / 4)
            code_ = ['mov esi, ebp']
            code_.append('add esi, '+offset)
            code_.append('add esi, ' + str(data_['size'] - 4))
            code_.append('mov cx, '+str(iters))
            code_.append(label + ':')
            code_.append('mov edx, [esi]')
            code_.append('push edx')
            code_.append('sub esi, 4')
            code_.append('dec cx')
            code_.append('jnz '+label)
            return code_

    def if_op(self, instr, scopeInfo, funcScope):
        var = instr[1]
        jLabel = instr[5]
        code = []
        flag = self.setFlags(instr, scopeInfo)

        varOffset = self.ebpOffset(var, scopeInfo[1], funcScope)
        code.append('mov edi, [ebp' + varOffset + ']')
        if flag[1] == 1:
            code.append('mov edi, [edi]')
        code.append('cmp edi, 0')
        code.append('je ' + jLabel)

        return code

    def goto_op(self, instr, scopeInfo, funcScope):
        jLabel = instr[1]
        code = []

        code.append('jmp ' + jLabel)
        return code

    def logical(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.setFlags(instr, scopeInfo)

        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        src1Offset = self.ebpOffset(src1, scopeInfo[2], funcScope)
        src2Offset = self.ebpOffset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        if flag[3] == 1:
            code.append('mov esi, [esi]')

        if instr[0] == '||':
            code.append('or edi, esi')
        elif instr[0] == '&&':
            code.append('and edi, esi')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def getRetVal(self, instr, scopeInfo, funcScope):
        data_ = helper.symbolTables[scopeInfo[1]].get(instr[1])
        baseType = helper.getBaseType(data_['type'])
        offset = self.ebpOffset(instr[1], scopeInfo[1], funcScope)

        self.counter += 1
        label = 'looping' + str(self.counter)
        iters = int(data_['size'] / 4)
        code_ = ['mov esi, ebp']
        code_.append('add esi, '+offset)
        code_.append('mov cx, '+str(iters))
        code_.append(label + ':')
        code_.append('mov edx, [eax]')
        code_.append('mov [esi], edx')
        code_.append('add esi, 4')
        code_.append('add eax, 4')
        code_.append('dec cx')
        code_.append('jnz '+label)
        return code_

    def inc_dec(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        dstOffset = self.ebpOffset(dst, scopeInfo[1], funcScope)
        flag = self.setFlags(instr, scopeInfo)
        
        code = []
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        if instr[0] == '++':
            code.append('inc esi')
        else:
            code.append('dec esi')

        if flag[1] == 1:
            code.append('mov edi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [edi], esi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], esi')
        return code

    def genCode(self, idx, funcScope):
        # Check instruction type and call function accordingly
        instr = self.code[idx]
        scopeInfo = self.scopeInfo[idx]

        if instr[0] == 'return':
            return []
        elif len(instr) == 1:
            return [instr[0]+':']
        elif instr[0] == '+int':
            return self.add_op(instr, scopeInfo, funcScope)
        elif instr[0] == '+float':
            return self.fadd_op(instr, scopeInfo, funcScope)
        elif instr[0] == '-float':
            return self.fsub_op(instr, scopeInfo, funcScope)
        if instr[0] == '-int':
            if len(instr) == 4:
                return self.sub_op(instr, scopeInfo, funcScope)
            else:
                return self.unary_minus(instr, scopeInfo, funcScope)
        if instr[0] == '*int':
            return self.mul_op(instr, scopeInfo, funcScope)
        if instr[0] == '*float':
            return self.fmul_op(instr, scopeInfo, funcScope)
        if instr[0] == '/int':
            return self.div_op(instr, scopeInfo, funcScope)


        if instr[0] == '=':
            return self.assign_op(instr, scopeInfo, funcScope)
        if instr[0] == '+=':
            return self.add_assign_op(instr, scopeInfo, funcScope)
        if instr[0] == '-=':
            return self.sub_assign_op(instr, scopeInfo, funcScope)
        if instr[0] == '*=':
            return self.mul_assign_op(instr, scopeInfo, funcScope)
        if instr[0] == '/=':
            return self.div_assign_op(instr, scopeInfo, funcScope)

        if instr[0] == 'retval':
            return self.getRetVal(instr, scopeInfo, funcScope)

        if instr[0] in self.relops:
            return self.relops_cmp(instr, scopeInfo, funcScope)

        if instr[0] == 'if':
            return self.if_op(instr, scopeInfo, funcScope)
        if instr[0] == 'goto':
            return self.goto_op(instr, scopeInfo, funcScope)

        if instr[0] in [ '||' , '&&']:
            return self.logical(instr, scopeInfo, funcScope)

        if instr[0] in ['--', '++']:
            return self.inc_dec(instr, scopeInfo, funcScope)

        if instr[0] == 'print_int':
            return self.print_int(instr, scopeInfo, funcScope)
        if instr[0] == 'print_float':
            return self.print_float(instr, scopeInfo, funcScope)
        elif instr[0] == 'scan_int':
            return self.scan_int(instr, scopeInfo, funcScope)
        elif instr[0] == 'param':
            return self.param(instr, scopeInfo, funcScope)
        elif instr[0] == 'call':
            # function call
            return ['call '+instr[1]]

        if instr[0] == '*pointer':
            return self.assign_ptr_rhs(instr, scopeInfo, funcScope)
        if instr[0][0] == '&':
            return self.ampersand_op(instr, scopeInfo, funcScope)

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
        elif code_[-1:] == ':' and 'main' in code_:
            outfile.write('main:\n')
        elif code_[-1:] == ':':
            outfile.write(code_ + '\n')
        else:
            outfile.write('    '+code_+'\n')
    outfile.close()
