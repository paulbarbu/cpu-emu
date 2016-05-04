from instr import OpCode, getOpcodeGroup, Group, AddrMode, encode_br, encode_other, encode_one_op, encode_two_op
from ast import literal_eval

class ParseError(Exception):
    pass

class Assembler(object):
    '''This class handles the loading and parsing of assembly files'''

    def __init__(self, filePath):
        '''Initialize the Assembler class

        Args:
            filePath - the path to the *.asm file to be loaded and parsed
        '''
        self.programText = []
        self.programCode = []
        self.lblToAddr = {}
        self.filePath = filePath


    def _validatePath(self):
        '''Load the assembly file
        The file must have .asm extension and the name shall not be empty

        Returns: True if the validation was successful, False otherwise
        '''
        if len(self.filePath) >=4 and len(self.filePath) - 4 != self.filePath.rfind('.asm'):
            return False

        return True


    def _sanitize(self, line):
        '''Remove comments, spaces, tabs and other useless data from the line passed as argument

        A comment starts with ; and lasts until the end of the line
        Multi-line comments do not exist

        Args:
            line - the line to remove comments from

        Returns:
            A string that has the same meaning as the one passed as argument, but without comments and whitespace
        '''
        comment_start = line.find(';')
        if -1 != comment_start:
            line = line[:comment_start]

        line = line.strip() # remove spaces from both ends
        # remove tabs & spaces from inside the string
        line = ' '.join(line.split('\t'))
        line = ' '.join(line.split(' '))

        return line


    def _parseOpcode(self, line):
        '''Parse an instruction opcode out of a line of assembly code

        Args:
            line - the assembly line

        Returns:
            A tuple representing the opcode and the instruction group: (opcode, group)
            Eg: (OpCode.MOV, Group.TWO_OP)
                (OpCode.BR, Group.BRANCH)

        Raises:
            ParseError - if an opcode cannot be parsed
        '''
        if len(line) < 1:
            raise ParseError('Invalid assembly line: ' + ' '.join(line))

        op = None

        for opcode in OpCode:
            if opcode.name.lower() == line[0].lower():
                op = opcode
                break

        if op is None:
            raise ParseError('Cannot find valid opcode for: ' + ' '.join(line))

        group = getOpcodeGroup(op)

        if group is None:
            raise ParseError('Cannot find valid instruction type for: ' + ' '.join(line))

        return (opcode, group)

    def _parseOperand(self, operand):
        '''Parse a single operand

        Args:
            operand - the operand to be parsed

        Returns:
            A tuple containing the addressing mode (AddrMode), the register (as a number) and the offset
            If one of the register number or offset doesn't apply, it will be 0
            Eg: R5: (AddrMode.DIRECT, 5, 0)

        Raises:
            ParseError - when the parsing fails
        '''
        mode = None
        r = 0
        offset = 0

        if len(operand) < 1:
            raise ParseError('Invalid operand: ' + operand)

        if operand[0].lower() == 'r': # direct access in register r
            r = self._parseLiteral(operand[1:])
            mode = AddrMode.DIRECT
            offset =0
        elif operand[0] == '(': # indirect or indexed access
            if operand[-1] == ')': # indirect access via register r
                if operand[1].lower() == 'r': # between the parens has to be a register
                    r = self._parseLiteral(operand[2:-1])
                    mode = AddrMode.INDIRECT
                    offset = 0
                else:
                    raise ParseError('Invalid operand {}, indirect access must be done with a register'
                        .format(operand))
            else: # indexed access with offset and register r
                close_paren_pos = operand.find(')')

                if -1 != close_paren_pos:
                    if operand[1].lower() == 'r': # between the parens has to be a register
                        r = self._parseLiteral(operand[2:close_paren_pos])
                        offset = self._parseLiteral(operand[close_paren_pos+1:])
                        mode = AddrMode.INDEXED
                    else:
                        raise ParseError('Invalid operand {}, indexed access must be done with a register'
                            .format(operand))
                else:
                    raise ParseError('Tried to parse indexed operand, but cannot find ")" in {}'.format(operand))
        else:
            offset = self._parseLiteral(operand)
            r = 0
            mode = AddrMode.IMMEDIATE

        return (mode, r, offset)


    def _parseLiteral(self, literal):
        try:
            return literal_eval(literal)
        except (ValueError, SyntaxError):
            raise ParseError('Cannot parse {} as a number'.format(literal))


    def _parseOperands(self, opcode, group, line):
        '''Parse the operands on a line, given the fact that we already know the opcode
        and the instruction's group

        Args:
            opcode - the opcode of the instruction
            group - the group of the instruction
            line - the line from where to parse the operands

        Raises:
            ParseError if the operands on the line cannot be parsed or if the instruction
            has invalid operands (eg: when operands are given to Group.OTHER instructions)
        '''
        err_msg = 'Opcode {} requires {} operands, given {} on line: {}'
        operands = line[1:]
        op_len = len(operands)
        encoded_op = None

        if group == Group.TWO_OP:
            if op_len != 2:
                raise ParseError(err_msg.format(opcode.name, 2, op_len, ' '.join(line)))

            (mad, rd, offsetd) = self._parseOperand(operands[0])
            (mas, rs, offsets) = self._parseOperand(operands[1])

            encoded_op = encode_two_op(opcode, mad, rd, mas, rs, offsetd, offsets)
        elif group == Group.ONE_OP:
            if op_len != 1:
                raise ParseError(err_msg.format(opcode.name, 1, op_len, ' '.join(line)))

            (ad, r, offset) = self._parseOperand(operands[0])

            encoded_op = encode_one_op(opcode, ad, r, offset)
        elif group == Group.BRANCH:
            if op_len != 1:
                raise ParseError(err_msg.format(opcode.name, 1, op_len, ' '.join(line)))

            (ad, r, offset) = self._parseOperand(operands[0])

            encoded_op = encode_br(opcode, offset)
        elif group == Group.OTHER:
            if op_len != 0:
                raise ParseError(err_msg.format(opcode.name, 0, op_len, ' '.join(line)))

            encoded_op = encode_other(opcode)
        else:
            raise ParseError('Invalid Group, this should never be reached')


        while len(encoded_op) < 3:
            encoded_op.append(0)
        self.programCode += encoded_op

    def _tokenize(self):
        '''Tokenize the program lines into its components

        Raises:
            ParseError - if the line is not standard assembly

            Standard assembly:
            OPCODE OP, OP
            OPCODE
            OPCODE OP
        '''
        tokenizedText = []

        for line in self.programText:
            split_line = line.split(' ', 1)

            #remove spaces from the arguments
            split_line = list(map(lambda x: x.replace(' ', ''), split_line))

            l = len(split_line)

            if l == 2: # instruction with one or two operands
                split_line = [split_line[0]] +  split_line[1].split(',')
            elif l > 2:
                raise ParseError('Invalid instruction: {}'.format(line))

            tokenizedText.append(split_line)

        self.programText = tokenizedText


    def _replaceLabels(self):
        '''Replace label names with addresses
        '''
        replacedText = []

        for line in self.programText:
            replaced_line = [line[0]]
            for token in line[1:]:
                replaced_token = token
                for k, v in self.lblToAddr.items():
                    if k == token:
                        # replace the label name with its address
                        replaced_token = str(v)
                        break

                replaced_line.append(replaced_token)

            replacedText.append(replaced_line)

        self.programText = replacedText


    def _labelsToAddr(self):
        '''Translate the labels found in code to real addresses'''
        ct = 0 # address counter
        definitionlessText = []

        #search for label definitions
        for line in self.programText:
            markIndex = line.find(':')

            if markIndex == len(line) - 1: # the whole line is just a label
                # store it without the ":"
                self.lblToAddr[line[:-1]] = ct
            elif markIndex != -1: # the line starts with a label
                self.lblToAddr[line[:markIndex]] = ct
                ct += 3
                definitionlessText.append(line[markIndex+1:].strip()) # remove the label from the line
            else: # there is no label definition on this line
                ct += 3
                definitionlessText.append(line.strip())

        print(self.lblToAddr)

        self.programText = definitionlessText


    def parse(self):
        '''Parse the loaded file
        Returns:
            The list of instructions that represent the program as encoded in memory
            If the program is empty, so will be the list
            If there is an error when parsing the file, a ParseError is raised
        '''
        if not self._validatePath():
            raise ParseError('Validation for {} failed'.format(self.filePath))

        with open(self.filePath) as f:
            for line in f:
                line = self._sanitize(line)
                if line != '':
                    self.programText.append(line)

        self.programText = list(filter(self._ignoreLine, self.programText))

        self._labelsToAddr()
        print(self.programText)

        self._tokenize()
        self._replaceLabels()

        for line in self.programText:
            print(line)
            (opcode, group) = self._parseOpcode(line)
            self._parseOperands(opcode, group, line)

        return self.programCode


    def _ignoreLine(self, line):
        '''Decides whether to ignore a line or not
        Should be used together with filter

        Args:
            line - the line that should be inspected

        Returns: False if the line should be ignored, True otherwise
        '''
        if line[0] == '.' or line == 'END':
            return False

        return True