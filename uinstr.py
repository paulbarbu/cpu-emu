from collections import OrderedDict

from enum import unique, IntEnum

@unique
class SBus(IntEnum):
    NONE = 0
    ZERO = 1
    REG = 2
    T = 3
    MDR = 4
    MINUS_ONE = 5
    IR_OFFSET = 6

SBUS_SIZE = 3

@unique
class DBus(IntEnum):
    NONE = 0
    PC = 1
    MDR = 2
    REG = 3
    ZERO = 4
    T = 5
    NOT_T = 6
    SP = 7
    FLAG = 8
    IVR = 9

DBUS_SIZE = 4

@unique
class RBus(IntEnum):
    NONE = 0
    ADR = 1
    T = 2
    MDR = 3
    REG = 4
    PC = 5
    FLAG = 6

RBUS_SIZE = 3

@unique
class Alu(IntEnum):
    NONE = 0
    SUM = 1
    AND = 2
    OR = 3
    XOR = 4
    ASL = 5
    ASR = 6
    LSR  = 7
    ROR = 8
    RLC = 9
    RRC = 10

ALU_SIZE = 4

@unique
class Misc(IntEnum):
    NONE = 0
    INC_PC = 1
    COND = 2 # set condition flags
    CIN_COND = 3 # set carry in and condition flags
    DEC_SP = 4
    INC_SP = 5
    SET_C = 6 # set carry flag
    SET_V = 7 # set overflow flag
    SET_Z = 8 # set zero flag
    SET_S = 9 # set sign flag
    CLEAR_C = 10
    CLEAR_V = 11
    CLEAR_Z = 12
    CLEAR_S = 13
    SET_FLAG = 14 # set all flags


MISC_SIZE = 4

@unique
class Mem(IntEnum):
    NONE = 0
    IFCH = 1
    READ = 2
    WRITE = 3

MEM_SIZE = 2

@unique
class Cond(IntEnum):
    TRUE = 0
    INT = 1
    NO_OP = 2 # no operand instruction
    ONE_OP = 3 # one operand instruction
    REG_DEST = 4 # destination is a register


@unique
class Index(IntEnum):
    NONE = 0
    MAD = 1 # IR 4, 5
    MAS = 2 # IR 10, 11
    OPCODE = 3 # IR 13 - 8
    ONE_OP = 4 # IR 13 - 6
    TWO_OP = 5 # IR 14 - 12

COND_SIZE = 3
ADDRESS_TRUE_SIZE = 7
ADDRESS_FALSE_SIZE = 7

INDEX_TRUE_SIZE = 3
INDEX_FALSE_SIZE = 3


SBUS_RIGHTPAD = DBUS_SIZE + ALU_SIZE + RBUS_SIZE + MISC_SIZE + MEM_SIZE + COND_SIZE + ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
DBUS_RIGHTPAD = ALU_SIZE + RBUS_SIZE + MISC_SIZE + MEM_SIZE + COND_SIZE + ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
ALU_RIGHTPAD = RBUS_SIZE + MISC_SIZE + MEM_SIZE + COND_SIZE + ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
RBUS_RIGHTPAD = MISC_SIZE + MEM_SIZE + COND_SIZE + ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
MISC_RIGHTPAD = MEM_SIZE + COND_SIZE + ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
MEM_RIGHTPAD = COND_SIZE + ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
COND_RIGHTPAD = ADDRESS_TRUE_SIZE + ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
AT_RIGHTPAD = ADDRESS_FALSE_SIZE + INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
AF_RIGHTPAD = INDEX_TRUE_SIZE + INDEX_FALSE_SIZE
IT_RIGHTPAD = INDEX_FALSE_SIZE

def size_to_bitmask(size):
    '''Get a number full of ones on the first size positions, eg:
    size = 4 -> 0b1111
    '''
    mask = 0
    for i in range(0, size):
        mask |= 2 ** i

    return mask


def build_uinstr(sbus=SBus.NONE, dbus=DBus.NONE, alu=Alu.NONE, rbus=RBus.NONE,
    misc=Misc.NONE, mem=Mem.NONE, cond=Cond.TRUE, address_true=1, address_false=0, index_true=Index.NONE,
    index_false=Index.NONE):
    '''Build a microinstruction out of its components'''
    return sbus << SBUS_RIGHTPAD | dbus << DBUS_RIGHTPAD | alu <<  ALU_RIGHTPAD \
        | rbus << RBUS_RIGHTPAD | misc << MISC_RIGHTPAD | mem << MEM_RIGHTPAD \
        | cond << COND_RIGHTPAD | address_true << AT_RIGHTPAD | address_false << AF_RIGHTPAD \
        | index_true << IT_RIGHTPAD | index_false


def getSBus(mir):
    '''Get the SBus field of the micro instruction'''
    return SBus(mir >> SBUS_RIGHTPAD)


def getDBus(mir):
    '''Get the DBus field of the micro instruction'''
    return DBus((mir >> DBUS_RIGHTPAD) & size_to_bitmask(DBUS_SIZE))


def getRBus(mir):
    '''Get the RBus field of the micro instruction'''
    return RBus((mir >> RBUS_RIGHTPAD) & size_to_bitmask(RBUS_SIZE))


def getMisc(mir):
    '''Get the Misc field of the micro instruction'''
    return Misc((mir >> MISC_RIGHTPAD) & size_to_bitmask(MISC_SIZE))


def getMem(mir):
    '''Get the Mem field of the micro instruction'''
    return Mem((mir >> MEM_RIGHTPAD) & size_to_bitmask(MEM_SIZE))


def getAlu(mir):
    '''Get the Alu field of the micro instruction'''
    return Alu((mir >> ALU_RIGHTPAD) & size_to_bitmask(ALU_SIZE))


def getCond(mir):
    '''Get the Cond field of the micro instruction'''
    return Cond((mir >> COND_RIGHTPAD) & size_to_bitmask(COND_SIZE))


def getAddressFalse(mir):
    '''Get the Address False field of the micro instruction'''
    return (mir >> AF_RIGHTPAD) & size_to_bitmask(ADDRESS_FALSE_SIZE)


def getIndexFalse(mir):
    '''Get the Index False field of the micro instruction'''
    return Index(mir & size_to_bitmask(INDEX_FALSE_SIZE))


def getAddressTrue(mir):
    '''Get the Address True field of the micro instruction'''
    return (mir >> AT_RIGHTPAD) & size_to_bitmask(ADDRESS_TRUE_SIZE)

def getIndexTrue(mir):
    '''Get the Index True field of the micro instruction'''
    return Index((mir >> IT_RIGHTPAD) & size_to_bitmask(INDEX_TRUE_SIZE))

def lbl2adr(mem, lbl):
    '''Get the address of a microinstruction in the microprogram memory (MPM)

    Args:
        mem - the dictionary representing the memory
        lbl - the key in the mem dict whose position we need to get
    Returns:
        The position at which we can find the needed label in the dictionary
    '''
    return mem.keys().index(lbl)


def adr2lbl(mem, adr):
    '''Get the label of a microinstruction in the microprogram memory (MPM)
    This should be the inverse of lbl2adr

    Args:
        mem - the dictionary representing the memory
        adr - the index returned by lbl2adr
    Returns:
        The label where we can find the mem[adr] data
    '''
    return list(mem.keys())[adr]


MPM = [
    #fetch instruction -> IR
    #'IFCH':
    build_uinstr(SBus.ZERO, DBus.PC, Alu.SUM, RBus.ADR, Misc.INC_PC, Mem.IFCH, Cond.NO_OP,
        #lbl2adr(MPM, 'BR'),
        65, 1, Index.OPCODE),
    #'IFCH1:':
    build_uinstr(cond=Cond.ONE_OP, #address_true=lbl2adr(MPM, 'IMMD'), address_false=lbl2adr(MPM, 'IMMS'),
        address_true=11, address_false=2, index_true=Index.MAD, index_false=Index.MAS),

    ### FETCH OPERAND(S)

    # immediate source -> T
    #'IMMS':
    build_uinstr(SBus.ZERO, DBus.PC, Alu.SUM, RBus.ADR, Misc.INC_PC, Mem.READ, Cond.TRUE, 3),
    #'IMMS3':
    build_uinstr(SBus.ZERO, DBus.MDR, Alu.SUM, RBus.T, Misc.NONE, Mem.NONE, Cond.TRUE,
        #lbl2adr(MPM, 'IMMD'),
        11, index_true=Index.MAD),

    # direct source - R5 -> T
    #TODO: DBus zero or none?
    #'DS':
    build_uinstr(SBus.REG, DBus.ZERO, Alu.SUM, RBus.T, Misc.NONE, Mem.NONE, Cond.TRUE,
        #lbl2adr(MPM, 'IMMD'),
        11, index_true=Index.MAD),
    #'DS5':
    build_uinstr(),

    # indirect source - (R7) -> T
    #TODO: DBus zero or none?
    #'IS':
    build_uinstr(SBus.REG, DBus.ZERO, Alu.SUM, RBus.ADR, Misc.NONE, Mem.READ, Cond.TRUE, 7),
    #'IS7':
    build_uinstr(SBus.ZERO, DBus.MDR, Alu.SUM, RBus.T, Misc.NONE, Mem.NONE, Cond.TRUE,
        #lbl2adr(MPM, 'IMMD'),
        11, index_true=Index.MAD),

    # indexed source - (R2)15 -> T
    #TODO: DBus zero or none?
    #'XS':
    build_uinstr(SBus.ZERO, DBus.PC, Alu.SUM, RBus.ADR, Misc.INC_PC, Mem.READ, Cond.TRUE, 9),
    #'XS9':
    build_uinstr(SBus.REG, DBus.MDR, Alu.SUM, RBus.ADR, Misc.NONE, Mem.READ, Cond.TRUE, 10),
    #'XS10':
    build_uinstr(SBus.ZERO, DBus.MDR, Alu.SUM, RBus.T, Misc.NONE, Mem.NONE, Cond.TRUE,
        #lbl2adr(MPM, 'IMMD'),
        11, index_true=Index.MAD),

    # immediate destination -> MDR
    #'IMMD':
    build_uinstr(SBus.ZERO, DBus.PC, Alu.SUM, RBus.ADR, Misc.INC_PC, Mem.READ, Cond.ONE_OP,
        #lbl2adr(MPM, 'CLR'), lbl2adr(MPM, 'MOV'),
        41, 27, Index.ONE_OP, Index.TWO_OP),
    #'IMMD12':
    build_uinstr(),

    # direct destination - R5 -> MDR
    #'DD':
    build_uinstr(SBus.ZERO, DBus.REG, Alu.SUM, RBus.MDR, Misc.NONE, Mem.NONE, Cond.ONE_OP,
        #lbl2adr(MPM, 'CLR'), lbl2adr(MPM, 'MOV'),
        41, 27, Index.ONE_OP, Index.TWO_OP),
    #'DD14':
    build_uinstr(),

    # indirect destination - (R5) -> MDR
    #'ID':
    build_uinstr(SBus.ZERO, DBus.REG, Alu.SUM, RBus.ADR, Misc.NONE, Mem.READ, Cond.ONE_OP,
        #lbl2adr(MPM, 'CLR'), lbl2adr(MPM, 'MOV'),
        41, 27, Index.ONE_OP, Index.TWO_OP),
    #'ID16':
    build_uinstr(),

    # indexed destination - (R5)42 -> MDR
    #'XD':
    build_uinstr(SBus.ZERO, DBus.PC, Alu.SUM, RBus.ADR, Misc.INC_PC, Mem.READ, Cond.TRUE, 18),
    #'XD18':
    build_uinstr(SBus.MDR, DBus.REG, Alu.SUM, RBus.ADR, Misc.NONE, Mem.READ, Cond.ONE_OP,
        #lbl2adr(MPM, 'CLR'), lbl2adr(MPM, 'MOV'),
        41, 27, Index.ONE_OP, Index.TWO_OP),

    ### MISC
    #'WRITE_MEM':
    build_uinstr(SBus.NONE, DBus.NONE, Alu.NONE, RBus.NONE, Misc.NONE, Mem.WRITE, Cond.INT,
        #lbl2adr(MPM, 'INT'), lbl2adr(MPM, 'IFCH')
        20, 0),

    #TODO: BVI
    #'INT':
    build_uinstr(SBus.ZERO, DBus.FLAG, Alu.SUM, RBus.MDR, Misc.DEC_SP, Mem.NONE, Cond.TRUE, 21),
    #'INT21':
    build_uinstr(SBus.ZERO, DBus.SP, Alu.SUM, RBus.ADR, Misc.NONE, Mem.WRITE, Cond.TRUE, 22),
    #'INT22':
    build_uinstr(SBus.ZERO, DBus.PC, Alu.SUM, RBus.MDR, Misc.DEC_SP, Mem.NONE, Cond.TRUE, 23),
    #'INT23':
    build_uinstr(SBus.ZERO, DBus.SP, Alu.SUM, RBus.ADR, Misc.NONE, Mem.WRITE, Cond.TRUE, 24),
    #'INT24':
    build_uinstr(SBus.ZERO, DBus.IVR, Alu.SUM, RBus.ADR, Misc.NONE, Mem.NONE, Cond.TRUE, 25),
    #'INT25':
    build_uinstr(SBus.NONE, DBus.NONE, Alu.NONE, RBus.NONE, Misc.NONE, Mem.READ, Cond.TRUE, 26),
    #'INT26':
    build_uinstr(SBus.MDR, DBus.ZERO, Alu.SUM, RBus.PC, Misc.NONE, Mem.NONE, Cond.TRUE,
        #lbl2adr(MPM, 'IFCH')
        0),

    ### TWO_OP instructions
    #TODO:  DBus NONE or ZERO?
    #'MOV':
    build_uinstr(SBus.T, DBus.NONE, Alu.SUM, RBus.MDR, Misc.NONE, Mem.NONE, Cond.REG_DEST, 28,
        #lbl2adr(MPM, 'WRITE_MEM')
        19),
    #'MOV_REG':
    build_uinstr(SBus.ZERO, DBus.MDR, Alu.SUM, RBus.REG, Misc.NONE, Mem.NONE, Cond.INT,
        #lbl2adr(MPM, 'INT'), lbl2adr(MPM, 'IFCH')
        20, 0),

    #ADD 29
    build_uinstr(SBus.T, DBus.MDR, Alu.SUM, RBus.MDR, Misc.COND, Mem.NONE, Cond.REG_DEST, 30, 19),
    build_uinstr(SBus.ZERO, DBus.MDR, Alu.SUM, RBus.REG, Misc.NONE, Mem.NONE, Cond.INT, 20, 0),

    #SUB 31
    build_uinstr(),
    build_uinstr(),

    #CMP 33
    build_uinstr(),
    build_uinstr(),

    #AND 35
    build_uinstr(),
    build_uinstr(),

    #OR 37
    build_uinstr(),
    build_uinstr(),

    #XOR 39
    build_uinstr(),
    build_uinstr(),

    ## ONE_OP instructions
    #'CLR' 41
    build_uinstr(SBus.NONE, DBus.NONE, Alu.NONE, RBus.NONE, Misc.NONE, Mem.NONE, Cond.REG_DEST, 42,
        #lbl2adr(MPM, 'WRITE_MEM')
        19),
    #'CLR_REG':
    build_uinstr(SBus.ZERO, DBus.NONE, Alu.SUM, RBus.REG, Misc.NONE, Mem.NONE, Cond.INT,
        #lbl2adr(MPM, 'INT'), lbl2adr(MPM, 'IFCH')
        20, 0),

    #NEG 43
    build_uinstr(),
    build_uinstr(),

    #INC 45
    build_uinstr(),
    build_uinstr(),

    #DEC 47
    build_uinstr(),
    build_uinstr(),

    #ASL 49
    build_uinstr(),
    build_uinstr(),

    #ASR 51
    build_uinstr(),
    build_uinstr(),

    #LSR 53
    build_uinstr(),
    build_uinstr(),

    #ROL 55
    build_uinstr(),
    build_uinstr(),

    #ROR 57
    build_uinstr(),
    build_uinstr(),

    #RLC 59
    build_uinstr(),
    build_uinstr(),

    #RRC 61
    build_uinstr(),
    build_uinstr(),

    #JMP 63
    build_uinstr(),
    build_uinstr(),

    ## BRANCH instructions
    #'BR' 65
    build_uinstr(SBus.IR_OFFSET, DBus.PC, Alu.SUM, RBus.PC, Misc.NONE, Mem.NONE, Cond.INT,
        #lbl2adr(MPM, 'INT'), lbl2adr(MPM, 'IFCH')
        20, 0),
    #'BR':
    build_uinstr(),

    #BNE
    build_uinstr(),
    build_uinstr(),

    #BEQ
    build_uinstr(),
    build_uinstr(),

    #BPL
    build_uinstr(),
    build_uinstr(),

    #BMI
    build_uinstr(),
    build_uinstr(),

    #BCS
    build_uinstr(),
    build_uinstr(),

    #BCC
    build_uinstr(),
    build_uinstr(),

    #BVS
    build_uinstr(),
    build_uinstr(),

    #BVC
    build_uinstr(),
    build_uinstr(),

    ## OTHER instructions
    #'CLC':
    build_uinstr(SBus.NONE, DBus.NONE, Alu.NONE, RBus.NONE, Misc.CLEAR_C, Mem.NONE, Cond.INT,
        #lbl2adr(MPM, 'INT'), lbl2adr(MPM, 'IFCH')
        20, 0),
    #'CLC':
    build_uinstr()

    #TODO: continue here
]