from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.surface.base import SurfaceArgument, SayContext, \
    SayResult


class SurfaceDirection(SurfaceArgument):
    def __init__(self, which, of):
        self.which = which
        assert self.which
        assert isinstance(self.which, str)

        self.of = of
        if self.of:
            assert isinstance(self.of, SurfaceArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'SurfaceDirection',
            'which': self.which,
            'of': self.of.dump() if self.of else None,
        }

    # --------------------------------------------------------------------------
    # From surface.

    def has_hole(self):
        return not self.of

    def put_fronted_arg_back(self, of):
        assert not self.of
        self.of = of

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        if self.of:
            sub_context = SayContext(
                ('of',), True, context.has_right, False)
            r = self.of.say(state, idiolect, sub_context)
            of_tokens = r.tokens
        else:
            of_tokens = []

        tokens = [self.which, 'of'] + of_tokens
        return SayResult(tokens=tokens, conjugation=Conjugation.S3,
                         eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        return SurfaceDirection(d['which'], loader.load(d['of']))
