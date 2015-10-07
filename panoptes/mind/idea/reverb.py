from panoptes.mind.idea.base import Idea


class Reverb(Idea):
    """
    Points back to an earlier idea.

    We create a new object for each new reference to the same earlier object in
    order for coreference resolution to work, which often depends on how "hot"
    references are.
    """

    def __init__(self, x):
        self.x = x

    def dump(self):
        return {
            'type': self.__class__.__name__,
            'x': self.x,
        }

    def matches_noun_view(self, view, ideas, place_kinds):
        n = ideas[self.x]
        return n.matches_noun_view(view, ideas, place_kinds)

    def matches_clause_view(self, view, ideas):
        c = ideas[self.x]
        return c.matches_clause_view(view, ideas)
