from enum import IntEnum, unique

class InvalidInstruction(Exception):
    pass


def getOpcodeGroup(opcode):
    '''Get an opcode's group

    Args:
        opcode - the OpCode for which the group should be returned

    Returns:
        The Group in which the opcode belongs: eg: TWO_OP, ONE_OP, etc
        None if the group cannot be determined
    '''
    group = None

    if Group.TWO_OP.value <= opcode.value < Group.BRANCH.value:
        group = Group.TWO_OP
    elif Group.BRANCH.value <= opcode.value < Group.ONE_OP.value:
        group = Group.BRANCH
    elif Group.ONE_OP.value <= opcode.value < Group.OTHER.value:
        group = Group.ONE_OP
    elif Group.OTHER.value <= opcode.value:
        group = Group.OTHER

    return group


def checkRegister(r, opcode):
    if r >= 16:
        raise InvalidInstruction('Valid register values: R0-R15, given {} to {}'
            .format(r, opcode.name))


def checkLiteral(val, opcode):
    if val >= 2**16:
        raise InvalidInstruction('Literal values should be smaller than 0x{:X}, given 0x{:X} to {}'
            .format(2**16, val, opcode.name))


def encode_other(opcode):
    '''Encode instructions that do not take operands

    Args:
        opcode - the opcode of the instruction

    Returns:
        The encoded instruction
    '''
    return [opcode]


def encode_br(opcode, offset):
    '''Encode branch instructions

    Args:
        opcode - the opcode of the instruction
        offset - the offset relative to the PC to jump to

    Returns:
        The encoded instruction
    '''
    if offset >= 2**8:
        raise InvalidInstruction('Branch instructions should use an offset smaller than 0x{:X}, given 0x{:X} to {}'
            .format(2**8, offset, opcode.name))

    return [opcode << 8 | offset]


def encode_one_op(opcode, ad, r, offset=0):
    '''Encode instructions with one operand

    Args:
        opcode - the opcode of the instruction
        ad - addressing mode
        r - source/destination register or 0 in case of immediate addr. mode
        offset - the offset from the value of the register in case of indexed addr. mode or immediate value

    Returns:
        The encoded instruction
    '''
    instr = []
    if AddrMode.IMMEDIATE == ad:
        valid_with_imm = [OpCode.JMP, OpCode.CALL, OpCode.PUSH]
        if opcode not in valid_with_imm:
            raise InvalidInstruction('Cannot use immediate addressing with {}'.format(opcode.name))

        checkLiteral(offset, opcode)

        instr = [(opcode << 6) | (ad << 4) | 0, offset]
    else:
        checkRegister(r, opcode)
        instr = [(opcode << 6) | (ad << 4) | r]

    if AddrMode.INDEXED == ad:
        checkLiteral(offset, opcode)
        instr.append(offset)

    return instr


def encode_two_op(opcode, mad, rd, mas, rs, offsetd=0, offsets=0):
    '''Encode instructions with two operands

    Args:
        opcode - the opcode of the instructions
        mad - destination addressing mode
        rd - destination register
        mas - source addressing mode
        rs - source register
        offsets - the offset from the value of the source register
            in case of indexed addr. mode
        offsetd - the offset from the value of the destination register
            in case of indexed addr. mode

    Returns:
        The encoded instruction
    '''
    valid_addr_modes = [
        #(SRC, DST)

        #(IMM, REG)
        (AddrMode.IMMEDIATE, AddrMode.DIRECT),
        #(IMM, MEM)
        (AddrMode.IMMEDIATE, AddrMode.INDIRECT),
        (AddrMode.IMMEDIATE, AddrMode.INDEXED),
        #(REG, REG)
        (AddrMode.DIRECT, AddrMode.DIRECT),
        #(REG, MEM)
        (AddrMode.DIRECT, AddrMode.INDIRECT),
        (AddrMode.DIRECT, AddrMode.INDEXED),
        #(MEM, REG)
        (AddrMode.INDIRECT, AddrMode.DIRECT),
        (AddrMode.INDEXED, AddrMode.DIRECT),
        #(MEM, MEM)
        (AddrMode.INDIRECT, AddrMode.INDIRECT),
        (AddrMode.INDIRECT, AddrMode.INDEXED),
        (AddrMode.INDEXED, AddrMode.INDEXED),
        (AddrMode.INDEXED, AddrMode.INDIRECT),
    ]

    if (mas, mad) not in valid_addr_modes:
        raise InvalidInstruction('Invalid addressing modes, source: {}, destination: {}, op: {}'
            .format(mas.name, mad.name, opcode.name))

    checkRegister(rs, opcode)
    checkRegister(rd, opcode)

    instr = [(opcode << 12) | (mas << 10) | (rs << 6) | (mad << 4) | rd]

    if AddrMode.INDEXED == mas or AddrMode.IMMEDIATE == mas:
        checkLiteral(offsets, opcode)
        instr.append(offsets)

    if AddrMode.INDEXED == mad:
        checkLiteral(offsetd, opcode)
        instr.append(offsetd)

    return instr


@unique
class AddrMode(IntEnum):
    IMMEDIATE = 0b00
    DIRECT = 0b01
    INDIRECT = 0b10
    INDEXED = 0b11


@unique
class Group(IntEnum):
    TWO_OP = 0x0
    ONE_OP = 0b1 << 9
    BRANCH = 0b11 << 6
    OTHER = 0b111 << 13


@unique
class OpCode(IntEnum):
    MOV = Group.TWO_OP | 0
    ADD = Group.TWO_OP | 1
    SUB = Group.TWO_OP | 2
    CMP = Group.TWO_OP | 3
    AND = Group.TWO_OP | 4
    OR = Group.TWO_OP | 5
    XOR = Group.TWO_OP | 6
    CLR = Group.ONE_OP | 7
    NEG = Group.ONE_OP | 8
    INC = Group.ONE_OP | 9
    DEC = Group.ONE_OP | 10
    ASL = Group.ONE_OP | 11
    ASR = Group.ONE_OP | 12
    LSR = Group.ONE_OP | 13
    ROL = Group.ONE_OP | 14
    ROR = Group.ONE_OP | 15
    RLC = Group.ONE_OP | 16
    RRC = Group.ONE_OP | 17
    JMP = Group.ONE_OP | 18
    CALL = Group.ONE_OP | 19
    PUSH = Group.ONE_OP | 20
    POP = Group.ONE_OP | 21
    BR = Group.BRANCH | 22
    BNE = Group.BRANCH | 23
    BEQ = Group.BRANCH | 24
    BPL = Group.BRANCH | 25
    BMI = Group.BRANCH | 26
    BCS = Group.BRANCH | 27
    BCC = Group.BRANCH | 28
    BVS = Group.BRANCH | 29
    BVC = Group.BRANCH | 30
    CLC = Group.OTHER | 31
    CLV = Group.OTHER | 32
    CLZ = Group.OTHER | 33
    CLS = Group.OTHER | 34
    CCC = Group.OTHER | 35
    SEC = Group.OTHER | 36
    SEV = Group.OTHER | 37
    SEZ = Group.OTHER | 38
    SES = Group.OTHER | 39
    SCC = Group.OTHER | 40
    NOP = Group.OTHER | 41
    RET = Group.OTHER | 42
    RETI = Group.OTHER | 43
    HALT = Group.OTHER | 44
    WAIT = Group.OTHER | 45
    PUSH_PC = Group.OTHER | 46
    POP_PC = Group.OTHER | 47
    PUSH_FLAG = Group.OTHER | 48
    POP_FLAG = Group.OTHER | 49