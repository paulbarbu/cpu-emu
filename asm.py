class ParseException(Exception):
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
            ParseException - if an opcode cannot be parsed
        '''
        pass


    def _labelsToAddr(self):
        '''Translate the labels found in code to real addresses'''
        ct = 0
        lblToAddr = {}
        definitionlessText = []
        newText = []

        #search for label definitions
        for line in self.programText:
            markIndex = line.find(':')

            if markIndex == len(line) - 1: # the whole line is just a label
                lblToAddr[line[:-1]] = ct
            elif markIndex != -1: # the line starts with a label
                lblToAddr[line[:markIndex]] = ct
                ct += 1
                definitionlessText.append(line[markIndex+1:]) # remove the label from the line
            else: # there is no label definition on this line
                ct += 1
                definitionlessText.append(line)

        for line in definitionlessText:
            replaced = False
            for k, v in lblToAddr.items():
                if k in line:
                    # replace the label name with its address
                    newText.append(line.replace(k, str(v)))
                    replaced = True
                    break

            if not replaced:
                newText.append(line)

        self.programText = newText


    def parse(self):
        '''Parse the loaded file
        Returns:
            The list of instructions that represent the program as encoded in memory
            If the program is empty, so will be the list
            If there is an error when parsing the file, a PrseException is raised
        '''
        if not self._validatePath():
            raise ParseError('Validation for {} failed'.format(self.filePath))

        try:
            with open(self.filePath) as f:
                for line in f:
                    line = self._sanitize(line)
                    if line != '':
                        self.programText.append(line)

            self.programText = list(filter(self._ignoreLine, self.programText))

            # for x in range(0,len(self.programText)):
            #     print(x, self.programText[x])

            self._labelsToAddr()
            print(self.programText)
        except Exception as e:
            print(e)
            return False

        return self.programCode

    def _ignoreLine(self, line):
        '''Decides whether to ignore a line or not
        Should be used together with filter

        Args:
            line - the line that should be inspected

        Returns: False if the line should be ignored, True otherwise
        '''
        if line[0] == '.':
            return False

        return True