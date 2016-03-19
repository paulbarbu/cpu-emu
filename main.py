#! /usr/bin/python3.5

from instr import *
from asm import Assembler

def showExampleEncodings():
    print('{:<20}\t{:>5}\t{:>10}'.format('Instr', 'Hex', 'Bin'))

    two_op_list = [
        ['MOV R0,R1', OpCode.MOV, AddrMode.DIRECT, 0, AddrMode.DIRECT, 1],
        ['MOV R4,(R2)', OpCode.MOV, AddrMode.DIRECT, 4, AddrMode.INDIRECT, 2],
        ['MOV (R3),124(R5)', OpCode.MOV, AddrMode.INDIRECT, 3, AddrMode.INDEXED, 5, 0, 124],
        ['ADD (R6),R0', OpCode.ADD, AddrMode.INDIRECT, 6, AddrMode.DIRECT, 0],
        ['SUB R3, R5', OpCode.SUB, AddrMode.DIRECT, 3, AddrMode.DIRECT, 5],
        ['CMP R0, (R1)', OpCode.CMP, AddrMode.DIRECT, 0, AddrMode.INDIRECT, 1],
        ['AND R2, R4', OpCode.AND, AddrMode.DIRECT, 2, AddrMode.DIRECT, 4],
        ['OR R1, (R5)', OpCode.OR, AddrMode.DIRECT, 1, AddrMode.INDIRECT, 5],
        ['XOR R3, R0', OpCode.XOR, AddrMode.DIRECT, 3, AddrMode.DIRECT, 0],
        ['XOR 123H, R0', OpCode.XOR, AddrMode.IMMEDIATE, 0x123, AddrMode.DIRECT, 3],
        ['XOR R0, 10000H', OpCode.XOR, AddrMode.DIRECT, 0, AddrMode.IMMEDIATE, 0, 0, 0x10000],
    ]

    one_op_list = [
        ['CLR (R0)', OpCode.CLR, AddrMode.INDIRECT, 0],
        ['NEG R3', OpCode.NEG, AddrMode.DIRECT, 3],
        ['INC (R2)', OpCode.INC, AddrMode.INDIRECT, 2],
        ['DEC R5', OpCode.DEC, AddrMode.DIRECT, 5],
        ['ASL R1', OpCode.ASL, AddrMode.DIRECT, 1],
        ['ASR (R2)', OpCode.ASR, AddrMode.INDIRECT, 2],
        ['LSR 14(R0)', OpCode.LSR, AddrMode.INDEXED, 0, 14],
        ['RLC R7', OpCode.RLC, AddrMode.DIRECT, 7],
        ['JMP 36(R1)', OpCode.JMP, AddrMode.INDEXED, 1, 36],
        ['CALL 1248H', OpCode.CALL, AddrMode.IMMEDIATE, 0, 0x1248],
        ['PUSH R3', OpCode.PUSH, AddrMode.DIRECT, 3],
        ['POP R5', OpCode.POP, AddrMode.DIRECT, 5],
        ['CLR 1248H', OpCode.CLR, AddrMode.IMMEDIATE, 0, 0x1248],
        ['JMP 15000H', OpCode.JMP, AddrMode.IMMEDIATE, 0, 0x15000],
        ['JMP (R17)', OpCode.JMP, AddrMode.INDEXED, 17, 0],
    ]

    br_list = [
        ['BR 99H', OpCode.BR, 0x99],
        ['BEQ 42H', OpCode.BEQ, 0x42],
        ['BR 2000H', OpCode.BEQ, 0x2000],
    ]

    other_list = [
        ['PUSH PC', OpCode.PUSH_PC],
        ['CLC', OpCode.CLC],
        ['NOP', OpCode.NOP],
    ]

    INSTR_TPL = '{0:<20}\t0x{1:04X}\t0b{1:016b}'

    print('Two operand instructions:')
    for op in two_op_list:
        try:
            op_encoded = encode_two_op(op[1], op[2], op[3], op[4], op[5], *op[6:])
            print(INSTR_TPL.format(op[0], op_encoded[0]))
            if len(op_encoded) > 0:
                for extra in op_encoded[1:]:
                    print(INSTR_TPL.format('', extra))
        except InvalidInstruction as e:
            print(op[0], e)

    print('One operand instructions:')
    for op in one_op_list:
        try:
            op_encoded = encode_one_op(op[1], op[2], op[3], *op[4:])
            print(INSTR_TPL.format(op[0], op_encoded[0]))
            if len(op_encoded) > 0:
                for extra in op_encoded[1:]:
                    print(INSTR_TPL.format('', extra))
        except InvalidInstruction as e:
            print(op[0], e)

    print('Branch instructions:')
    for op in br_list:
        try:
            op_encoded = encode_br(op[1], op[2])
            print(INSTR_TPL.format(op[0], op_encoded[0]))
            if len(op_encoded) > 0:
                for extra in op_encoded[1:]:
                    print(INSTR_TPL.format('', extra))
        except InvalidInstruction as e:
            print(op[0], e)

    print('Other instructions:')
    for op in other_list:
        try:
            op_encoded = encode_other(op[1])
            print(INSTR_TPL.format(op[0], op_encoded[0]))
            if len(op_encoded) > 0:
                for extra in op_encoded[1:]:
                    print(INSTR_TPL.format('', extra))
        except InvalidInstruction as e:
            print(op[0], e)


def showOpCodes():
    print('{:<10}\t{:>10}\t{:>20}'.format('OpCode', 'Hex', 'Bin'))
    for name, member in OpCode.__members__.items():
        print('{:<10}\t{:>10}\t{:>20}'.format(name, hex(member.value), bin(member.value)))


if __name__ == '__main__':
    showOpCodes()
    showExampleEncodings()
    print()
    asm = Assembler('examples/factorial.asm')
    #asm = Assembler('examples/mul.asm')
    #asm = Assembler('examples/int.asm')
    print(asm.parse())