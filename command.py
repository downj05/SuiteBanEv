class Command:
    def __init__(self, name:str, callback:function, help:str=None, usage:str=None):
        self.name = name
        self.callback = callback
        self.help = help
        self.usage = usage
    
class CommandsList:
    def __init__(self):
        self._commands = []

    def register(self, command: Command):
        self._commands.append(command)
    
    def handle_input(self, input: str):
        