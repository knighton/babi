from panoptes.ling.tree.common.existential_there import ExistentialThere
from panoptes.ling.tree.common.personal_pronoun import PersonalPronoun
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.deep.common_noun import DeepCommonNoun
from panoptes.ling.tree.deep.content_clause import DeepContentClause
from panoptes.ling.tree.surface.common_noun import SurfaceCommonNoun
from panoptes.ling.tree.surface.content_clause import SurfaceContentClause


class ArgLoader(object):
    """
    Layer of indirection for loading a syntactic tree from a dict.

    Tree objects can be recursive (contain other trees of a variety of types).
    We call out to this, which bounces back into the child tree's load()
    method once we know what kind of tree it is.
    """

    def __init__(self):
        classes = [
            # Deep.
            DeepCommonNoun,
            DeepContentClause,

            # Common.
            ExistentialThere,
            PersonalPronoun,
            ProperNoun,

            # Surface.
            SurfaceCommonNoun,
            SurfaceContentClause,
        ]

        self.type2load = {}
        for c in classes:
            self.type2load[c.__name__] = c.load

    def load(self, d):
        if d is None:
            return d

        type = d['type']
        return self.type2load[type](d)
