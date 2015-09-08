from ling.tree.surface.content_clause import ContentClause


class Sentence(object):
    def __init__(self, root, end_punct):
        self.root = root
        assert isinstance(self.root, ContentClause)

        self.end_punct = end_punct
        assert isinstance(self.end_punct, str)

    def say(self, state, idiolect):
        has_left = False
        has_right = False
        prep = None
        is_pos = False
        is_arg = False
        context = SayContext(
            idiolect, has_left, has_right, prep, is_pos, is_arg)
        r = self.root.say(state, context)
        return r.tokens + [self.end_punct]
