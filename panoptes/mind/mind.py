from panoptes.mind.know.memory import Memory
from panoptes.mind.know.user import UserManager
from panoptes.mind.verb.manager import VerbSemanticsManager


class Mind(object):
    def __init__(self):
        self.memory = Memory()
        self.user_mgr = UserManager(self.memory)
        self.semantics_mgr = VerbSemanticsManager(self.memory)

    def new_user(self):
        return self.user_mgr.new()

    def overhear(self, dsen, from_uids, to_uids):
        checkpoint = self.memory.make_checkpoint()

        from_xx = map(self.user_mgr.get, from_uids)
        to_xx = map(self.user_mgr.get, to_uids)
        xx = self.memory.decode_dsen(dsen, from_xx, to_xx)

        if not xx:
            self.memory.load_checkpoint(checkpoint)
            return None

        x, = xx
        c = self.memory.ideas[x]
        r = self.semantics_mgr.handle(c)

        if not r:
            self.memory.load_checkpoint(checkpoint)
            return None

        return r
