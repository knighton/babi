from ling.english import English


class Agent(object):
    def __init__(self):
        self.en = English()

    def put(self, text):
        for dsen in self.en.each_dsen_from_text(text):
            print '[[', dsen
