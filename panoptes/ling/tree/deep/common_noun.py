from panoptes.ling.glue.relation import RelationArgType
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.common_noun import CommonNoun as \
    SurfaceCommonNoun


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

    def relation_arg_type(self):
        return RelationArgType.INERT

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

    def to_surface(self, state, idiolect):
        if self.possessor:
            possessor = self.possessor.to_surface(idiolect)
        else:
            possessor = None

        if self.explicit_number:
            explicit_number = self.explicit_number.to_surface(idiolect)
        else:
            explicit_number = None

        attributes = map(lambda a: a.to_surface(idiolect), self.attributes)

        preps_nargs = []
        for rel, arg in self.rels_nargs:
            arg_type = arg.relation_arg_type()
            prep = state.relation_mgr.get(rel).decide_prep(arg_type)
            narg = arg.to_surface(idiolect)
            preps_nargs.append((prep, narg))

        return SurfaceCommonNoun(
            possessor, self.correlative, self.gram_number, self.gram_of_number,
            explicit_number, attributes, self.noun, self.say_noun, preps_nargs)
