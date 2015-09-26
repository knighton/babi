from random import randint

from panoptes.agent.agent import Agent


class PhilosophicalZombie(Agent):
    def __init__(self):
        self.reset()

    def reset(self):
        self.user_ids_set = set()

    def new_user(self):
        uid = randint(0, 0x7FFFFFFFFFFFFFFF)
        assert uid not in self.user_ids_set
        self.user_ids_set.add(uid)
        return uid

    def put(uid, text):
        assert uid in self.user_ids_set
        return text
