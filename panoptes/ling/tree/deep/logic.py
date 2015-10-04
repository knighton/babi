from panoptes.ling.tree.deep.base import DeepArgument


class DeepAnd(DeepArgument):
    def __init__(self, aa):
        self.aa = aa

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        dd = []
        for a in self.aa:
            dd.append(a.dump())
        return {
            'type': 'DeepConjunction',
            'aa': dd,
        }

    def is_interrogative(self):
        return any(map(lambda a: a.is_interrogative(), self.aa))

    def is_relative(self):
        return any(map(lambda a: a.is_relative(), self.aa))

    # --------------------------------------------------------------------------
    # From deep.

    def to_surface(self, transform_state, say_state, idiolect):
        surfs = []
        for deep in self.aa:
            surf = deep.to_surface(transform_state, say_state, idiolect)
            surfs.append(surf)
        return SurfaceAnd(surfs)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        aa = []
        for j in d['aa']:
            a = loader.load(j)
            aa.append(a)
        return DeepAnd(aa)
