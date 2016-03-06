#! /usr/bin/python3.5

from instr import *

def showExampleEncodings():
    print('{:<20}\t{:>10}\t{:>20}'.format('Instr', 'Hex', 'Bin'))

    op_list = [
        ['MOV R0,R1', OpCode.MOV, AddrMode.DIRECT, 0, AddrMode.DIRECT, 1],
        ['MOV R4,(R2)', OpCode.MOV, AddrMode.DIRECT, 4, AddrMode.INDIRECT, 2],
        ['MOV (R3),124(R5)', OpCode.MOV, AddrMode.INDIRECT, 3, AddrMode.INDEXED, 5],
        ['ADD (R6),R0', OpCode.ADD, AddrMode.INDIRECT, 6, AddrMode.DIRECT, 0],
        ['SUB R3, R5', OpCode.SUB, AddrMode.DIRECT, 3, AddrMode.DIRECT, 5],
        ['CMP R0, (R1)', OpCode.CMP, AddrMode.DIRECT, 0, AddrMode.INDIRECT, 1],
        ['AND R2, R4', OpCode.AND, AddrMode.DIRECT, 2, AddrMode.DIRECT, 4],
        ['OR R1, (R5)', OpCode.OR, AddrMode.DIRECT, 1, AddrMode.INDIRECT, 5],
        ['XOR R3, R0', OpCode.XOR, AddrMode.DIRECT, 3, AddrMode.DIRECT, 0],
    ]

    for op in op_list:
        op_encoded = encode(op[1], op[2], op[3], op[4], op[5])
        print('{0:<20}\t0x{1:016X}\t0b{1:016b}'.format(op[0], op_encoded))


def showOpCodes():
    print('{:<10}\t{:>10}\t{:>20}'.format('OpCode', 'Hex', 'Bin'))
    for name, member in OpCode.__members__.items():
        print('{:<10}\t{:>10}\t{:>20}'.format(name, hex(member.value), bin(member.value)))


if __name__ == '__main__':
    showOpCodes()
    showExampleEncodings()