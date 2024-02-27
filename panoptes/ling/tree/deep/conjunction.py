from panoptes.ling.glue.conjunction import Conjunction
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.conjunction import SurfaceConjunction


class DeepConjunction(DeepArgument):
    def __init__(self, op, aa):
        self.op = op
        assert Conjunction.is_valid(self.op)

        self.aa = aa
        assert isinstance(self.aa, list)
        for a in self.aa:
            assert isinstance(a, DeepArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        jj = []
        for a in self.aa:
            jj.append(a.dump())
        return {
            'type': self.__class__.__name__,
            'op': Conjunction.to_str[self.op],
            'aa': jj,
        }

    # --------------------------------------------------------------------------
    # From deep.

    def to_surface(self, transform_state, say_state, idiolect):
        aa = [a.to_surface(transform_state, say_state, idiolect) for a in self.aa]
        return SurfaceConjunction(self.op, aa)

    # --------------------------------------------------------------------------
    # Static.

    def load(j, loader):
        op = Conjunction.from_str[j['op']]
        aa = []
        for sub_j in j['aa']:
            a = loader.load(sub_j)
            aa.append(a)
        return DeepConjunction(op, aa)
