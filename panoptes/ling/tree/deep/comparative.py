from panoptes.ling.morph.comparative.comparative import ComparativePolarity
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.comparative import SurfaceComparative


class DeepComparative(DeepArgument):
    def __init__(self, polarity, adjective, than):
        self.polarity = polarity
        assert ComparativePolarity.is_valid(self.polarity)

        self.adjective = adjective
        assert self.adjective
        assert isinstance(self.adjective, str)

        self.than = than
        assert isinstance(self.than, DeepArgument)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'DeepComparative',
            'polarity': ComparativePolarity.to_str[self.polarity],
            'adjective': self.adjective,
            'than': self.than.dump() if self.than else None,
        }

    # --------------------------------------------------------------------------
    # From deep.

    def to_surface(transform_state, say_state, idiolect):
        than = self.than.to_surface(transform_state, say_state, idiolect)
        return SurfaceDirection(self.polarity, self.adjective, than)

    # --------------------------------------------------------------------------
    # Static.

    def load(d, loader):
        polarity = ComparativePolarity.from_str[d['polarity']]
        adjective = d['adjective']
        than = loader.load(d['than'])
        return DeepDirection(polarity, adjective, than)
