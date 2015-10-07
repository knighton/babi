class Idea(object):
    def dump(self):
        raise NotImplementedError

    def matches_noun_view(self, view, ideas, place_kinds):
        return False

    def matches_clause_view(self, view):
        return False
