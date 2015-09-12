from panoptes.ling.tree.surface.content_clause import ContentClause


class Sentence(object):
    def __init__(self, root, end_punct):
        self.root = root
        assert isinstance(self.root, ContentClause)

        self.end_punct = end_punct
        assert isinstance(self.end_punct, str)

    def say(self, state, idiolect):
        context = SayContext(prep=None, has_left=False, has_right=False,
                             is_possessive=False)
        r = self.root.say(state, idiolect, context)
        return r.tokens + [self.end_punct]
