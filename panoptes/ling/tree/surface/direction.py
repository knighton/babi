from panoptes.ling.tree.surface.base import SurfaceArgument, SayContext, \
    SayResult


class SurfaceDirection(SurfaceArgument):
    def __init__(self, which, of):
        self.which = which
        assert self.which
        assert isinstance(self.which, basestring)

        self.of = of
        if self.of:
            assert isinstance(self.of, SurfaceArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'which': self.which,
            'of': self.of.dump() if self.of else None,
        }

    # --------------------------------------------------------------------------
    # From surface.

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
