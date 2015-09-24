from panoptes.ling.glue.grammatical_number import N3, N5
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.common_noun import SurfaceCommonNoun


class DeepCommonNoun(DeepArgument):
    def __init__(self, possessor, gram_number, number, attributes, noun,
                 say_noun, rels_nargs):
        self.possessor = possessor
        if self.possessor:
            assert isinstance(self.possessor, DeepArgument)
            assert gram_number.is_definite()

        self.gram_number = gram_number
        assert isinstance(self.gram_number, CommonNounGrammaticalNumber)

        self.number = number
        assert not self.number  # NOTE: not in demo.

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

    def dump(self):
        if self.possessor:
            pos = self.possessor.dump()
        else:
            pos = None

        if self.explicit_number:
            num = self.explicit_number.dump()
        else:
            num = None

        rels_nargs = []
        for rel, arg in self.rels_nargs:
            rel = Relation.to_str[rel]
            arg = arg.dump()
            rels_nargs.append((rel, arg))

        return {
            'type': 'DeepCommonNoun',
            'possessor': pos,
            'gram_number': self.gram_number.dump(),
            'number': num,
            'attributes': map(lambda a: a.dump(), self.attributes),
            'noun': self.noun,
            'say_noun': self.say_noun,
            'rels_nargs': rels_nargs,
        }

    def is_interrogative(self):
        if self.gram_number.is_interrogative():
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

    def to_surface(self, transform_state, say_state, idiolect):
        if self.possessor:
            pos = self.possessor.to_surface(transform_state, say_state,
                                            idiolect)
        else:
            pos = None

        if self.number:
            num = self.number.to_surface(transform_state, say_state, idiolect)
        else:
            num = None

        attributes = map(
            lambda a: a.to_surface(transform_state, say_state, idiolect),
            self.attributes)

        preps_nargs = []
        for rel, arg in self.rels_nargs:
            arg_type = arg.relation_arg_type()
            prep = transform_state.relation_mgr.get(rel).decide_prep(arg_type)
            narg = arg.to_surface(transform_state, say_state, idiolect)
            preps_nargs.append([prep, narg])

        return SurfaceCommonNoun(pos, self.gram_number, num, attributes,
                                 self.noun, self.say_noun, preps_nargs)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        pos = loader.load(d['possessor'])
        gram_number = CommonNounGrammaticalNumber.load(d['gram_number'])
        num = loader.load(d['number'])
        attributes = map(loader.load, d['attributes'])
        noun = d['noun']
        say_noun = d['say_noun']

        rels_nargs = []
        for rel, arg in d['rels_nargs']:
            rel = Relation.from_str[rel]
            arg = loader.load(arg)
            rels_nargs.append((rel, arg))

        return DeepCommonNoun(pos, gram_number, num, attributes, noun, say_noun,
                              rels_nargs)
