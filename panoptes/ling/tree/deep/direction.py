from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.direction import SurfaceDirection


class DeepDirection(DeepArgument):
    def __init__(self, which, of):
        self.which = which
        assert self.which
        assert isinstance(self.which, basestring)

        self.of = of
        if self.of:
            assert isinstance(self.of, DeepArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'DeepDirection',
            'which': self.which,
            'of': self.of.dump() if self.of else None,
        }

    # --------------------------------------------------------------------------
    # From deep.

    def to_surface(transform_state, say_state, idiolect):
        if self.of:
            of = self.of.to_surface(transform_state, say_state, idiolect)
        else:
            of = None
        return SurfaceDirection(self.which, of)

    # --------------------------------------------------------------------------
    # Static.

    def load(d, loader):
        return DeepDirection(d['which'], loader.load(d['of']))
