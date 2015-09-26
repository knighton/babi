from random import randint

from panoptes.agent.agent import Agent
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
        dsens = list(self.english.each_dsen_from_text(text))
        if not dsens:
            return

        dsen = dsens[0]
        import json
        print '>>>', text
        print json.dumps(dsen.dump(), indent=4, sort_keys=True)

        r = self.mind.overhear(dsen, [from_uid], [self.bot_uid])
        if not r:
            return

        return self.english.say(r)

    def put(self, from_uid, text):
        dsens = list(self.english.each_dsen_from_text(text))
        if not dsens:
            return

        dsen = dsens[0]
        import json
        print json.dumps(dsen.dump(), indent=4, sort_keys=True)

        r = self.mind.overhear(dsen, [from_uid], [self.bot_uid])
        if not r:
            return

        return self.english.say(r)
