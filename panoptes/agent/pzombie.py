from random import randint

from panoptes.agent.agent import Agent, Deliberation
from panoptes.ling.english import English
from panoptes.mind.mind import Mind, OverhearResult


class PhilosophicalZombie(Agent):
    def __init__(self):
        # Static state.
        self.english = English()

        # Dynamic state.
        self.reset()

    def reset(self):
        self.mind = Mind()
        self.self_uid = self.mind.new_user()

    def new_user(self):
        return self.mind.new_user()

    def put(self, from_uid, text):
        recog = self.english.recognize(text)
        delib = Deliberation(recog)

        if not delib.recognized.dsens:
            return delib

        for dsen in delib.recognized.dsens:
            r = self.mind.overhear(dsen, [from_uid], [self.self_uid])

            # Returns None if it rejected the input dsen.
            if not r:
                continue

            # Else, r.out contains the output, which may be None.
            # if r.out:
            #     delib.out = self.english.say(r.out)
            delib.out = r.text
            return delib

        # Enable this assert to require everything to be understood by the
        # system, including funky parses.  Useful for development.
        # assert delib.out is not None

        return delib
