from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.morph.comparative.comparative import ComparativeDegree, \
    ComparativePolarity
from panoptes.ling.tree.surface.base import SurfaceArgument, SayContext, \
    SayResult


class SurfaceComparative(SurfaceArgument):
    def __init__(self, polarity, adjective, than):
        self.polarity = polarity
        assert ComparativePolarity.is_valid(self.polarity)

        self.adjective = adjective
        assert self.adjective
        assert isinstance(self.adjective, basestring)

        self.than = than
        if self.than:
            assert isinstance(self.than, SurfaceArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'SurfaceComparative',
            'polarity': ComparativePolarity.to_str[self.polarity],
            'adjective': self.adjective,
            'than': self.than.dump() if self.than else None,
        }

    # --------------------------------------------------------------------------
    # From surface.

    def has_hole(self):
        return not self.than

    def put_fronted_arg_back(self, than):
        assert not self.than
        self.than = than

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        if self.than:
            sub_context = SayContext(
                ('than',), True, context.has_right, False)
            r = self.than.say(state, idiolect, sub_context)
            than_tokens = r.tokens
        else:
            than_tokens = []

        pre, main = state.comparative_mgr.encode(
            ComparativeDegree.COMPARATIVE, self.polarity, self.adjective)

        tokens = []
        if pre:
            tokens.append(pre)
        assert main
        tokens.append(main)
        tokens.append('than')
        tokens += than_tokens

        return SayResult(tokens=tokens, conjugation=Conjugation.S3,
                         eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        polarity = ComparativePolarity.from_str[d['polarity']]
        adjective = d['adjective']
        than = loader.load(d['than'])
        return SurfaceComparative(polarity, adjective, than)
