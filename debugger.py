from seq import ExecEnd
import readline

class Debugger(object):
    """The Debugger allows the user to step through the micro-code"""
    def __init__(self, seq):
        """ Instantiate the Debugger class

        Args:
            seq - the seq that should be run
        """
        super(Debugger, self).__init__()
        self.seq = seq
        self.actions = {
            'stop': ['q', 'quit', 'exit', 'stop'],
            'continue': ['c', 'continue', 'cont', 'run'],
            'step': ['s', 'step'],
            'display cpu state': ['d', 'display', 'p', 'print'],
            'display memory': ['m', 'mem', 'memory'],
            'display flags': ['f', 'flags', 'flag'],
            'display registers': ['r', 'reg', 'registers'],
            'display help': ['h', 'help'],
        }

    def getHelp(self):
        '''Display a list of available commands'''
        cmds = ''
        for k, v in self.actions.items():
            cmds += '{}: {}\n'.format(k, ', '.join(v))
        return 'Available commands:\n{}'.format(cmds)

    def attach(self):
        '''Start the seq by attaching the debugger'''

        action = self.actions['step'][0]
        try:
            while action not in self.actions['stop']:
                last_action = action
                action = input('> ')

                if action == '':
                    action = last_action

                if action in self.actions['continue']:
                    while True:
                        self.seq.execMicroInstr()
                elif action in self.actions['step']:
                    self.seq.execMicroInstr()
                elif action in self.actions['display cpu state']:
                    print(self.seq.showCpu())
                elif action in self.actions['display memory']:
                    print(self.seq.showMem())
                elif action in self.actions['display flags']:
                    print(self.seq.showFlags())
                elif action in self.actions['display registers']:
                    print(self.seq.showReg())
                elif action in self.actions['display help']:
                    print(self.getHelp())
                elif action not in self.actions['stop']:
                    print('Unknown action, use "h" to get help, "q" to quit')

        except ExecEnd:
            print(self.seq.showCpu())
