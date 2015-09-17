import json

from panoptes.ling.english import English


class Agent(object):
    def __init__(self):
        self.english = English()

    def put(self, text):
        print '[Agent.put]', '=' * 80
        for dsen in self.english.each_dsen_from_text(text):
            print '[Agent] Got dsen:'
            print json.dumps(dsen.dump(), indent=4, sort_keys=True)
