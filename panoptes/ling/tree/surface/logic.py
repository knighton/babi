from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.surface.base import SayContext, SayResult, \
    SurfaceArgument


class SurfaceConjunction(SurfaceArgument):
    def __init__(self, aa):
        raise NotImplementedError

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        dd = []
        for a in self.aa:
            dd.append(a.dump())
        return {
            'type': self.__class__.__name__,
            'aa': dd,
        }

    def is_interrogative(self):
        return any(map(lambda a: a.is_interrogative(), self.aa))

    def is_relative(self):
        return any(map(lambda a: a.is_relative(), self.aa))

    # --------------------------------------------------------------------------
    # From surface.

    def has_hole(self):
        return any(map(lambda a: a.has_hole(), self.aa))

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
                tokens += [self.text]

        return SayResult(tokens=tokens, conjugation=Conjugation.P3,
                         eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        aa = []
        for j in d['aa']:
            a = loader.load(j)
            aa.append(a)
        return DeepAnd(aa)


class SurfaceAllOf(SurfaceConjunction):
    """
    And.
    """

    def __init__(self, aa):
        self.aa = aa
        self.text = 'and'


class SurfaceOneOf(SurfaceConjunction):
    """
    Either-or.
    """

    def __init__(self, aa):
        self.aa = aa
        self.text = 'or'
