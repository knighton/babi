from ling.tree.surface.content_clause import ContentClause


class Sentence(object):
    def __init__(self, root, end_punct):
        self.root = root
        assert isinstance(self.root, ContentClause)

        self.end_punct = end_punct
        assert isinstance(self.end_punct, str)
