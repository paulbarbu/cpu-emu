from uinstr import *
from instr import *
import pdb

class ExecEnd(Exception):
    pass


class Cpu(object):
    '''Holds the CPU state'''
    def __init__(self, memory):
        '''Init the CPU states'''
        self.ir = -1
        self.pc = 0
        self.sp = 0

        self.mem = memory
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
        REG_TPL = 'R{0}:\t0x{1:04X}\t0b{1:016b}\t{1}\n'
        retval = '{:<5}\t{:>5}\t{:>10}\t{:>11}\n'.format('Reg', 'Hex', 'Bin', 'Dec')

        for i in range(0,16):
            retval += REG_TPL.format(i, self.r[i])

        return retval

    def _flagsToStr(self):
        FLAG_TPL = '{0:<10}:\t{1}\n'
        retval = '{:<5}\t{:>12}\n'.format('Flag', 'Val')

        retval += FLAG_TPL.format('(Z)ero', self.z)
        retval += FLAG_TPL.format('(C)arry', self.c)
        retval += FLAG_TPL.format('O(v)erflow', self.v)
        retval += FLAG_TPL.format('(S)ign', self.s)

        return retval

    def __str__(self):
        return self._regToStr() + self. _flagsToStr()

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
            self.cpu.sbus = getBrOffset(self.cpu.ir)
        elif sbus == SBus.MINUS_ONE:
            self.cpu.sbus = -1
        elif sbus == SBus.ONE:
            self.cpu.sbus = 1
        else:
            self.cpu.sbus = None
        #TODO: continue here

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
        else:
            self.cpu.dbus = None
        #TODO: continue here

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
            pdb.set_trace()
            self.cpu.pc = val
        elif rbus == RBus.NONE:
            pass

        #TODO: continue here FLAG = 6

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
        elif op == Misc.NONE:
            pass
            #TODO: continue here


    def execMem(self, mem):
        if mem == Mem.IFCH:
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

        return rval * 2

    def run(self):
        '''Run the CPU
        '''
        while True:
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


