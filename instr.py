from enum import IntEnum, unique

class InvalidInstruction(Exception):
    pass

def encode_one_op(opcode, ad, r, offset=0):
    '''Encode instructions with one operand

    Args:
        opcode - the opcode of the instruction
        ad - addressing mode
        r - source/destination register or immediate value
        offset - the offset from the value of the register in case of indexed addr. mode

    Returns:
        The encoded instruction
    '''
    instr = []
    if AddrMode.IMMEDIATE == ad:
        valid_with_imm = [OpCode.JMP, OpCode.CALL, OpCode.PUSH]
        if opcode not in valid_with_imm:
            raise InvalidInstruction('Cannot use immediate addressing with {}'.format(opcode.name))

        instr = [(opcode << 6) | (ad << 4) | 0, r]
    else:
        instr = [(opcode << 6) | (ad << 4) | r]

    if AddrMode.INDEXED == ad:
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

    instr = [(opcode << 12) | (mas << 10) | (rs << 6) | (mad << 4) | rd]

    if AddrMode.INDEXED == mad:
        instr.append(offsetd)

    if AddrMode.INDEXED == mas:
        instr.append(offsets)

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