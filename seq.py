from uinstr import *
from instr import *
import pdb

class ExecEnd(Exception):
    pass


class Cpu(object):
    '''Holds the CPOU state'''
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
        self.rbus = 0

        #TODO bvi


class Seq(object):
    '''Implements the sequencer automaton for a given CPU and microprogram memory'''
    def __init__(self, mpm, cpu):
        '''Init the class as if the computer just booted up'''
        self.mir = None # micro instruction register
        self.mar = 0 # micro instruction address register
        self.mpm = mpm # micro program memory
        self.cpu = cpu

    def setSBus(self, sbus):
        if sbus == SBus.NONE or sbus == SBus.ZERO:
            self.cpu.sbus = 0
        elif sbus == SBus.REG:
            self.cpu.rIndex = getRs(self.cpu.ir)
            self.cpu.sbus = self.cpu.r[self.cpu.rIndex]
        elif sbus == SBus.T:
            self.cpu.sbus = self.cpu.t
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
        elif rbus == RBus.NONE:
            pass
        #TODO: continue here

    def execAlu(self, op):
        rval = None

        if op == Alu.NONE:
            pass
        elif op == Alu.SUM:
            rval = self.cpu.sbus + self.cpu.dbus
            #TODO: continue here

        return rval

    def execMisc(self, op):
        if op == Misc.INC_PC:
            self.cpu.pc += 1
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
        elif mem == Mem.NONE:
            pass
            #TODO: continue here

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

            #TODO: continue here
        return rval

    def indexToOffset(self, index):
        rval = 0

        if index == Index.NONE:
            pass
        elif index == Index.MAS:
            rval = getMas(self.cpu.ir) * 2
        elif index == Index.MAD:
            rval = getMad(self.cpu.ir) * 2

        #TODO: continue here
        return rval

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

            #pdb.set_trace()
            adr = 0
            index =0
            if self.testCond(getCond(self.mir)):
                adr = getAddressTrue(self.mir)
                index = self.indexToOffset(getIndexTrue(self.mir))
            else:
                adr = getAddressFalse(self.mir)
                index = self.indexToOffset(getIndexFalse(self.mir))

            # the addresses in the MPM are absolute
            self.mar = adr + index


