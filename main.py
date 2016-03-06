#! /usr/bin/python3.5

from instr import *

def showExampleEncodings():
    print('{:<10}\t{:>10}\t{:>20}'.format('Instr', 'Hex', 'Bin'))
    mov_R0_R1 = encode(OpCode.MOV, AddrMode.DIRECT, 0, AddrMode.DIRECT, 1)
    print('{:<10}\t0x{:016X}\t{:016b}'.format('MOV R0,R1', mov_R0_R1, mov_R0_R1))
    mov_R4_xR2 = encode(OpCode.MOV, AddrMode.DIRECT, 4, AddrMode.INDIRECT, 2)
    print('{:<10}\t0x{:016X}\t{:016b}'.format('MOV R0,R1', mov_R4_xR2, mov_R4_xR2))


def showOpCodes():
    print('{:<10}\t{:>10}\t{:>20}'.format('OpCode', 'Hex', 'Bin'))
    for name, member in OpCode.__members__.items():
        print('{:<10}\t{:>10}\t{:>20}'.format(name, hex(member.value), bin(member.value)))


if __name__ == '__main__':
    showOpCodes()
    showExampleEncodings()