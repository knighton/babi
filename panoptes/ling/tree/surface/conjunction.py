from panoptes.etc.dicts import v2k_from_k2v
from panoptes.etc.enum import enum
from panoptes.ling.glue.conjunction import Conjunction
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.surface.base import SayContext, SayResult, \
    SurfaceArgument


class SurfaceConjunction(SurfaceArgument):
    def __init__(self, op, aa):
        self.op = op
        assert Conjunction.is_valid(self.op)

        self.aa = aa
        assert isinstance(self.aa, list)
        for a in self.aa:
            assert isinstance(a, SurfaceArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        dd = []
        for a in self.aa:
            dd.append(a.dump())
        return {
            'type': self.__class__.__name__,
            'op': Conjunction.to_str[self.op],
            'aa': dd,
        }

    def is_interrogative(self):
        return any([a.is_interrogative() for a in self.aa])

    def is_relative(self):
        return any([a.is_relative() for a in self.aa])

    # --------------------------------------------------------------------------
    # From surface.

    def has_hole(self):
        return any([a.has_hole() for a in self.aa])

    def put_fronted_arg_back(self, n):
        for a in self.aa:
            try:
                a.put_fronted_arg_back(n)
                return
            except:
                pass
        assert False

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.P3

    def say(self, state, idiolect, context):
        tokens = []
        for i, a in self.aa:
            if i == 0:
                left = context.has_left
            else:
                left = True

            if i == len(self.aa) - 1:
                right = True
            else:
                right = context.has_right

            sub_context = SayContext(
                context.prep, has_left=left, has_right=right,
                is_possessive=False)
            r = a.say(state, idiolect, sub_context)
            tokens += r.tokens

            if i < len(self.aa) - 2:
                tokens += [',']
            if i != len(self.aa) - 1:
                tokens += [OP2TEXT[self.op]]

        return SayResult(tokens=tokens, conjugation=Conjugation.P3,
                         eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        op = Conjunction.from_strs[d['op']]
        aa = []
        for j in d['aa']:
            a = loader.load(j)
            aa.append(a)
        return DeepAnd(op, aa)
