from panoptes.ling.tree.deep.base import DeepArgument


class CommonNoun(DeepArgument):
    def __init__(self, possessor, correlative, gram_number, gram_of_number,
                 explicit_number, attributes, noun, say_noun, rels_nargs):
        self.possessor = possessor
        if self.possessor:
            assert isinstance(self.possessor, DeepArgument)
            assert correlative == DeepCorrelative.DEFINITE

        self.correlative = correlative
        self.gram_number = gram_number
        self.gram_of_number = gram_of_number
        assert DeepCorrelative.is_valid(self.correlative)
        assert N3.is_valid(self.gram_number)
        assert N5.is_valid(self.gram_of_number)

        self.explicit_number = explicit_number
        if self.explicit_number:
            assert False  # TODO: not in demo.

        self.attributes = attributes
        assert isinstance(self.attributes, list)
        for a in self.attributes:
            assert False  # TODO: not in demo.

        self.noun = noun
        self.say_noun = say_noun
        if self.say_noun or self.noun:
            assert isinstance(self.noun, basestring)
            assert self.noun

        self.rels_nargs = rels_nargs
        for r, n in self.rels_nargs:
            assert False  # TODO: not in demo.

    def is_interrogative(self):
        if self.correlative == DeepCorrelative.INTR:
            return True

        if self.possessor:
            if self.possessor.is_interrogative():
                return True

        return False

    def is_relative(self):
        if self.possessor:
            if self.possessor.is_relative():
                return True

        for r, n in self.rels_nargs:
            if n and n.is_relative():
                return True

        return False
