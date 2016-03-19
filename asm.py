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

        Raises:
            ParseError - if an opcode cannot be parsed
        '''
        #TODO: use enum_member.name to identify what I need
        pass


    def _tokenize(self):
        '''Tokenize the program lines into its components

        Raises:
            ParseError - if the line is not standard assembly:
            OPCODE OP,OP
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
                ct += 1
                definitionlessText.append(line[markIndex+1:].strip()) # remove the label from the line
            else: # there is no label definition on this line
                ct += 1
                definitionlessText.append(line.strip())

        print(self.lblToAddr)

        self.programText = definitionlessText


    def parse(self):
        '''Parse the loaded file
        Returns:
            The list of instructions that represent the program as encoded in memory
            If the program is empty, so will be the list
            If there is an error when parsing the file, a PrseException is raised
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
            #self._parseOpcode(line)

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