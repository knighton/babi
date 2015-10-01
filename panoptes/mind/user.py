from random import randint

from panoptes.mind.idea import Noun


class UserManager(object):
    def __init__(self, memory):
        self.memory = memory
        self.uid2x = {}

    def new(self):
        uid = randint(0, 0x7FFFFFFFFFFFFFFF)
        assert uid not in self.uid2x
        x = self.memory.add_idea(Noun(kind='person'))
        self.uid2x[uid] = x
        return uid

    def get(self, uid):
        return self.uid2x[uid]
