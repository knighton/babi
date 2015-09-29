from random import randint

from panoptes.agent.agent import Agent, Deliberation
from panoptes.ling.english import English
from panoptes.mind.mind import Mind


class PhilosophicalZombie(Agent):
    def __init__(self):
        # Static state.
        self.english = English()

        # Dynamic state.
        self.reset()

    def reset(self):
        self.mind = Mind()
        self.bot_uid = self.mind.new_user()

    def new_user(self):
        return self.mind.new_user()

    def put(self, from_uid, text):
        recog = self.english.recognize(text)
        delib = Deliberation(recog)

        if not delib.recognized.dsens:
            return None, delib

        dsen = delib.recognized.dsens[0]

        r = self.mind.overhear(dsen, [from_uid], [self.bot_uid])
        if not r:
            return None, delib

        # return self.english.say(r), delib
        return r, delib
