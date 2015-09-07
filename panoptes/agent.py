from ling.english import English


class Agent(object):
    def __init__(self):
        self.english = English()

    def put(self, text):
        for dsen in self.english.each_dsen_from_text(text):
            print '[[', dsen
