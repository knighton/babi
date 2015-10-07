class Idea(object):
    def dump(self):
        raise NotImplementedError

    def matches_noun_features(self, f, ideas, place_kinds):
        return False

    def matches_clause_features(self, f, ideas):
        return False
