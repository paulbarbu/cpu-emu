from uinstr import *
from instr import *

import pdb

class ExecEnd(Exception):
    pass

class StackOverflow(Exception):
    pass

class Cpu(object):
    '''Holds the CPU state'''
    def __init__(self, memory):
        '''Init the CPU states'''
        self.STACK_SIZE = 32
        self.mem = memory + [0] * self.STACK_SIZE
        self.STACK_LIMIT = len(self.mem)

        self.sp = self.STACK_LIMIT
        self.ir = -1
        self.pc = 0

        self.adr = -1
        self.mdr = -1

        self.t = -1

        self.r = [-1] * 16
        self.rIndex = -1

        self.ivr = 0
        self.intr = False

        self.z = False
        self.c = False
        self.v = False
        self.s = False

        self.sbus = 0
        self.dbus = 0
        #TODO bvi

    def _regToStr(self):
        REG_TPL = 'R{0}:\t0x{1:04X}\t0b{1:016b}\t{2}\n'
        retval = '{:<5}\t{:>5}\t{:>10}\t{:>11}\n'.format('Reg', 'Hex', 'Bin', 'Dec')

        for i in range(0,16):
            retval += REG_TPL.format(i, self._toTwosComplement(self.r[i]), self.r[i])

        return retval

    def _memToStr(self):
        MEM_TPL = '{0:04X}:\t0x{1:04X}\t0b{1:016b}\t{2}\n'
        retval = '{:<5}\t{:>5}\t{:>10}\t{:>11}\n'.format('Adr', 'Hex', 'Bin', 'Dec')

        for i in range(0,len(self.mem) - self.STACK_SIZE):
            retval += MEM_TPL.format(i, self._toTwosComplement(self.mem[i]), self.mem[i])

        retval += 'Stack:\n'
        for i in range(len(self.mem) - self.STACK_SIZE, len(self.mem)):
            retval += MEM_TPL.format(i, self._toTwosComplement(self.mem[i]), self.mem[i])

        return retval

    def _flagsToStr(self):
        FLAG_TPL = '{0:<10}:\t{1}\n'
        retval = '{:<5}\t{:>12}\n'.format('Flag', 'Val')

        retval += FLAG_TPL.format('(Z)ero', self.z)
        retval += FLAG_TPL.format('(C)arry', self.c)
        retval += FLAG_TPL.format('O(v)erflow', self.v)
        retval += FLAG_TPL.format('(S)ign', self.s)

        return retval

    def _internalStateToStr(self):
        STATE_TPL = '{0}:\t0x{1:04X}\t0b{1:016b}\t{2}\n'
        retval = '{:<5}\t{:>12}\n'.format('Reg', 'Val')

        retval += STATE_TPL.format('IR', self._toTwosComplement(self.ir), self.ir)
        retval += STATE_TPL.format('PC', self._toTwosComplement(self.pc), self.pc)
        retval += STATE_TPL.format('T', self._toTwosComplement(self.t), self.t)
        retval += STATE_TPL.format('ADR', self._toTwosComplement(self.adr), self.adr)
        retval += STATE_TPL.format('MDR', self._toTwosComplement(self.mdr), self.mdr)
        retval += STATE_TPL.format('SP', self._toTwosComplement(self.sp), self.sp)

        return retval

    def __str__(self):
        return self._regToStr() + self. _flagsToStr() + self._memToStr() + self._internalStateToStr()

    def _toTwosComplement(self, x, num_bits=16):
        '''Turn a number to its two's complement representation

            Args:
                x: the number to be represented in two's complement
                num_bits: the number of bits the number is represented on

            Returns: the number in two's complements
        '''
        twos_complement = x
        if x < 0:
            twos_complement = x + 2 ** num_bits

        return twos_complement


class Seq(object):
    '''Implements the sequencer automaton for a given CPU and microprogram memory'''
    def __init__(self, mpm, cpu):
        '''Init the class as if the computer just booted up'''
        self.mir = None # micro instruction register
        self.mar = 0 # micro instruction address register
        self.mpm = mpm # micro program memory

        self.cpu = cpu

        self.z = False
        self.c = False
        self.v = False
        self.s = False

    def setSBus(self, sbus):
        if sbus == SBus.NONE or sbus == SBus.ZERO:
            self.cpu.sbus = 0
        elif sbus == SBus.REG:
            self.cpu.rIndex = getRs(self.cpu.ir)
            self.cpu.sbus = self.cpu.r[self.cpu.rIndex]
        elif sbus == SBus.T:
            self.cpu.sbus = self.cpu.t
        elif sbus == SBus.MDR:
            self.cpu.sbus = self.cpu.mdr
        elif sbus == SBus.IR_OFFSET:
            # BRs are relative to the current PC
            self.cpu.sbus = getBrOffset(self.cpu.ir) - self.cpu.pc
        elif sbus == SBus.MINUS_ONE:
            self.cpu.sbus = -1
        elif sbus == SBus.ONE:
            self.cpu.sbus = 1
        else:
            self.cpu.sbus = None

    def setDBus(self, dbus):
        if dbus == DBus.NONE or dbus == DBus.ZERO:
            self.cpu.dbus = 0
        elif dbus == DBus.PC:
            self.cpu.dbus = self.cpu.pc
        elif dbus == DBus.REG:
            self.cpu.rIndex = getRd(self.cpu.ir)
            self.cpu.dbus = self.cpu.r[self.cpu.rIndex]
        elif dbus == DBus.MDR:
            self.cpu.dbus = self.cpu.mdr
        elif dbus == DBus.NOT_MDR:
            self.cpu.dbus = ~self.cpu.mdr
        elif dbus == DBus.T:
            self.cpu.dbus = self.cpu.t
        elif dbus == DBus.SP:
            self.cpu.dbus = self.cpu.sp
        else:
            self.cpu.dbus = None

    def setRBus(self, rbus, val):
        if rbus == RBus.ADR:
            self.cpu.adr = val
        elif rbus == RBus.T:
            self.cpu.t = val
        elif rbus == RBus.MDR:
            self.cpu.mdr = val
        elif rbus == RBus.REG:
            self.cpu.r[self.cpu.rIndex] = val
        elif rbus == RBus.PC:
            self.cpu.pc = val
        elif rbus == RBus.NONE:
            pass

    def execAlu(self, op):
        rval = None

        if op == Alu.NONE:
            pass
        elif op == Alu.SUM:
            rval = self.cpu.sbus + self.cpu.dbus
        elif op == Alu.SUB:
            rval = self.cpu.sbus - self.cpu.dbus
        elif op == Alu.AND:
            rval = self.cpu.sbus & self.cpu.dbus
        elif op == Alu.OR:
            rval = self.cpu.sbus | self.cpu.dbus
        elif op == Alu.XOR:
            rval = self.cpu.sbus ^ self.cpu.dbus
        elif op == Alu.ASL:
            rval = self.cpu.dbus << 1
        elif op == Alu.ASR:
            rval = self.cpu.dbus >> 1
            #TODO: continue here

        if rval != None:
            self.z = rval == 0
            self.s = rval < 0

        #TODO: set carry & overflow

        return rval

    def execMisc(self, op):
        if op == Misc.INC_PC:
            self.cpu.pc += 1
        if op == Misc.CLEAR_C:
            self.cpu.c = False
        elif op == Misc.COND:
            self.cpu.z = self.z
            self.cpu.c = self.c
            self.cpu.v = self.v
            self.cpu.s = self.s
        elif op == Misc.SET_C:
            self.cpu.c = True
        elif op == Misc.SET_V:
            self.cpu.v = True
        elif op == Misc.SET_Z:
            self.cpu.z = True
        elif op == Misc.SET_S:
            self.cpu.s = True
        elif op == Misc.CLEAR_C:
            self.cpu.c = False
        elif op == Misc.CLEAR_V:
            self.cpu.v = False
        elif op == Misc.CLEAR_Z:
            self.cpu.z = False
        elif op == Misc.CLEAR_S:
            self.cpu.s = False
        elif op == Misc.SET_FLAG:
            self.cpu.c = True
            self.cpu.v = True
            self.cpu.s = True
            self.cpu.z = True
        elif op == Misc.CLEAR_FLAG:
            self.cpu.c = False
            self.cpu.v = False
            self.cpu.s = False
            self.cpu.z = False
        elif op == Misc.INC_SP:
            self.cpu.sp += 1
        elif op == Misc.DEC_SP:
            if self.cpu.sp > self.cpu.STACK_LIMIT - self.cpu.STACK_SIZE:
                self.cpu.sp -= 1
            else:
                raise StackOverflow()
        elif op == Misc.NONE:
            pass

    def execMem(self, mem):
        if mem == Mem.IFCH:
            if self.cpu.pc >= self.cpu.STACK_LIMIT - self.cpu.STACK_SIZE:
                raise ExecEnd() # do not execute code from the stack
            try:
                self.cpu.ir = self.cpu.mem[self.cpu.pc]
            except IndexError:
                raise ExecEnd()
        elif mem == Mem.READ:
            self.cpu.mdr = self.cpu.mem[self.cpu.adr]
        elif mem == Mem.WRITE:
            self.cpu.mem[self.cpu.adr] = self.cpu.mdr
        elif mem == Mem.NONE:
            pass

    def testCond(self, cond):
        rval = True

        if cond == Cond.TRUE:
            pass
        elif cond == Cond.NO_OP:
            group = getOpcodeGroup(getOpcode(self.cpu.ir))
            rval = group != Group.ONE_OP and group != Group.TWO_OP
        elif cond == Cond.ONE_OP:
            group = getOpcodeGroup(getOpcode(self.cpu.ir))
            rval = group == Group.ONE_OP
        elif cond == Cond.REG_DEST:
            rval = AddrMode.DIRECT == AddrMode(getMad(self.cpu.ir))
        elif cond == Cond.INT:
            rval = self.cpu.intr
        elif cond == Cond.Z:
            rval = self.cpu.z
        elif cond == Cond.NZ:
            rval = not self.cpu.z
        elif cond == Cond.S:
            rval = self.cpu.s
        elif cond == Cond.NS:
            rval = not self.cpu.s
        elif cond == Cond.V:
            rval = self.cpu.v
        elif cond == Cond.NV:
            rval = not self.cpu.v
        elif cond == Cond.C:
            rval = self.cpu.c
        elif cond == Cond.NC:
            rval = not self.cpu.c

        return rval

    def indexToOffset(self, index):
        rval = None

        if index == Index.NONE:
            rval = 0
        elif index == Index.MAS:
            rval = getMas(self.cpu.ir)
        elif index == Index.MAD:
            rval = getMad(self.cpu.ir)
        elif index == Index.OPCODE:
            # get the offset between the current instruction and the BR one
            # this implies that the MPM must have the same order as the instructions appear
            # in the enums
            br_ir = encode_br(OpCode.BR, 0)[0]
            rval = (getOpcodeNoGroup(self.cpu.ir) - getOpcodeNoGroup(br_ir))
        elif index == Index.ONE_OP:
            # get the offset between the current instruction and the CLR one
            # this implies that the MPM must have the same order as the instructions appear
            # in the enums
            one_op_ir = encode_one_op(OpCode.CLR, AddrMode.DIRECT, 0)[0]
            rval = (getOpcodeNoGroup(self.cpu.ir) - getOpcodeNoGroup(one_op_ir))
        elif index == Index.TWO_OP:
            # get the offset between the current instruction and the MOVE one
            # this implies that the MPM must have the same order as the instructions appear
            # in the enums
            two_op_ir = encode_two_op(OpCode.MOV, AddrMode.DIRECT, 0, AddrMode.DIRECT, 0)[0]
            rval = (getOpcodeNoGroup(self.cpu.ir) - getOpcodeNoGroup(two_op_ir))

        rval *= 2
        # the CALL microroutie has 4 (not 2) micro-instructions, so I need to shift the rest in that group by 2
        if index == Index.ONE_OP and \
            getOpcodeNoGroup(self.cpu.ir) > getOpcodeNoGroup(encode_one_op(OpCode.CALL, AddrMode.IMMEDIATE, 0)[0]):
            rval += 2
        return rval

    def execMicroInstr(self):
        '''Execute a microinstruction'''
        self.mir = self.mpm[self.mar]

        self.setSBus(getSBus(self.mir))
        self.setDBus(getDBus(self.mir))
        alu_res = self.execAlu(getAlu(self.mir))
        self.setRBus(getRBus(self.mir), alu_res)
        self.execMem(getMem(self.mir))
        self.execMisc(getMisc(self.mir))

        adr = 0
        index = 0
        if self.testCond(getCond(self.mir)):
            adr = getAddressTrue(self.mir)
            index = self.indexToOffset(getIndexTrue(self.mir))
        else:
            adr = getAddressFalse(self.mir)
            index = self.indexToOffset(getIndexFalse(self.mir))

        # the addresses in the MPM are absolute
        self.mar = adr + index

    def showMem(self):
        return self.cpu._memToStr()

    def showReg(self):
        return self.cpu._regToStr()

    def showFlags(self):
        return self.cpu._flagsToStr()

    def showCpu(self):
        return str(self.cpu)

    def showInternalState(self):
        return str(self.cpu._internalStateToStr())


