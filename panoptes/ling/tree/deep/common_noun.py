from panoptes.ling.glue.correlative import SurfaceCorrelative
from panoptes.ling.glue.relation import RelationArgType
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.common_noun import SurfaceCommonNoun


class DeepCommonNoun(DeepArgument):
    def __init__(self, possessor, correlative, gram_number, gram_of_number,
                 explicit_number, attributes, noun, say_noun, rels_nargs):
        self.possessor = possessor
        if self.possessor:
            assert isinstance(self.possessor, DeepArgument)
            assert correlative == SurfaceCorrelative.DEF

        self.correlative = correlative
        self.gram_number = gram_number
        self.gram_of_number = gram_of_number
        assert SurfaceCorrelative.is_valid(self.correlative)
        assert N3.is_valid(self.gram_number)
        assert N5.is_valid(self.gram_of_number)

        self.explicit_number = explicit_number
        if self.explicit_number:
            assert False  # NOTE: not in demo.

        self.attributes = attributes
        assert isinstance(self.attributes, list)
        for a in self.attributes:
            assert False  # NOTE: not in demo.

        self.noun = noun
        self.say_noun = say_noun
        if self.say_noun or self.noun:
            assert isinstance(self.noun, basestring)
            assert self.noun

        self.rels_nargs = rels_nargs
        for r, n in self.rels_nargs:
            assert False  # NOTE: not in demo.

    # --------------------------------------------------------------------------
    # From base.

    def to_d(self):
        if self.possessor:
            pos = self.possessor.to_d()
        else:
            pos = None

        if self.explicit_number:
            num = self.explicit_number.to_d()
        else:
            num = None

        rels_nargs = []
        for rel, arg in self.rels_nargs:
            rel = Relation.to_str[rel]
            arg = arg.to_d()
            rels_nargs.append((rel, arg))

        return {
            'type': 'DeepCommonNoun',
            'possessor': pos,
            'correlative': SurfaceCorrelative.to_str[self.correlative],
            'gram_number': N3.to_str[self.gram_number],
            'gram_of_number': N5.to_str[self.gram_of_number],
            'explicit_number': num,
            'attributes': map(lambda a: a.to_d(), self.attributes),
            'noun': self.noun,
            'say_noun': self.say_noun,
            'rels_nargs': rels_nargs,
        }

    def is_interrogative(self):
        if self.correlative == SurfaceCorrelative.INTR:
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

    # --------------------------------------------------------------------------
    # From deep.

    def relation_arg_type(self):
        return RelationArgType.INERT

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

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def from_d(d, recursion):
        possessor = recursion.from_d(d['possessor'])
        correlative = SurfaceCorrelative.from_str[d['correlative']]
        gram_number = N3.from_str[d['gram_number']]
        gram_of_number = N5.from_str[d['gram_of_number']]
        explicit_number = recursion.from_d(d['explicit_number'])
        attributes = map(recursion.from_d, d['attributes'])
        noun = d['noun']
        say_noun = d['say_noun']

        rels_nargs = []
        for rel, arg in d['rels_nargs']:
            rel = Relation.from_str[rel]
            arg = recursion.from_d(arg)
            rels_nargs.append((rel, arg))

        return DeepCommonNoun(
            possessor, correlative, gram_number, gram_of_number,
            explicit_number, attributes, noun, say_noun, rels_nargs)
