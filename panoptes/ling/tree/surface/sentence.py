from panoptes.ling.tree.surface.base import SayContext
from panoptes.ling.tree.surface.content_clause import SurfaceContentClause


class SurfaceSentence(object):
    def __init__(self, root, end_punct):
        self.root = root
        assert isinstance(self.root, SurfaceContentClause)

        self.end_punct = end_punct
        assert isinstance(self.end_punct, str)

    def say(self, state, idiolect):
        context = SayContext(prep=None, has_left=False, has_right=False,
                             is_possessive=False)
        r = self.root.say(state, idiolect, context)
        return r.tokens + [self.end_punct]
