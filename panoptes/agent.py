from ling.parse.parser import Parser


class Agent(object):
    def __init__(self):
        self.parser = Parser()

    def put(self, text):
        parses = self.parser.parse(text)
        return None
