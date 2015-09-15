from panoptes.ling.tree.deep.content_clause import DeepContentClause
from panoptes.ling.tree.surface.sentence import SurfaceSentence


class DeepSentence(object):
    def __init__(self, root):
        self.root = root
        assert isinstance(self.root, DeepContentClause)
        # TODO: actuality = actual, etc (clause-allowable-at-root checks).

    def dump(self):
        return {
            'root': self.root.to_d(),
        }

    def to_surface(self, state, idiolect):
        surf_root = self.root.to_surface(state, idiolect)
        end_punct = self.root.decide_end_punct()
        return SurfaceSentence(surf_root, end_punct)

    @staticmethod
    def load(d, loader):
        root = loader.load(d['root'])
        return DeepSentence(root)
