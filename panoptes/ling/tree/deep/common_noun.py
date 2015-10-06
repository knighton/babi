from panoptes.ling.glue.grammatical_number import N3, N5
from panoptes.ling.tree.common.util.selector import Selector
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.common_noun import SurfaceCommonNoun


class DeepCommonNoun(DeepArgument):
    def __init__(self, possessor=None, selector=None, number=None,
                 attributes=None, noun=None, rels_nargs=None):
        if attributes is None:
            attributes = []
        if rels_nargs is None:
            rels_nargs = []

        self.possessor = possessor
        if self.possessor:
            assert isinstance(self.possessor, DeepArgument)
            assert selector.is_definite()

        self.selector = selector
        assert isinstance(self.selector, Selector)

        self.number = number

        self.attributes = attributes
        assert isinstance(self.attributes, list)
        for s in self.attributes:
            assert s
            assert isinstance(s, basestring)

        self.noun = noun
        if self.noun:
            assert isinstance(self.noun, basestring)
            assert self.noun

        self.rels_nargs = rels_nargs
        for r, n in self.rels_nargs:
            assert False  # NOTE: not in demo.

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        if self.possessor:
            possessor = self.possessor.dump()
        else:
            possessor = None

        if self.number:
            number = self.number.dump()
        else:
            number = None

        rels_nargs = []
        for rel, arg in self.rels_nargs:
            rel = Relation.to_str[rel]
            arg = arg.dump()
            rels_nargs.append((rel, arg))

        return {
            'type': 'DeepCommonNoun',
            'possessor': possessor,
            'selector': self.selector.dump(),
            'number': number,
            'attributes': self.attributes,
            'noun': self.noun,
            'rels_nargs': rels_nargs,
        }

    def is_interrogative(self):
        if self.selector.is_interrogative():
            return True

        if self.number and self.number.is_interogative():
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
            possessor = self.possessor.to_surface(transform_state, say_state,
                                                  idiolect)
        else:
            possessor = None

        if self.number:
            number = self.number.to_surface(transform_state, say_state,
                                            idiolect)
        else:
            number = None

        preps_nargs = []
        for rel, arg in self.rels_nargs:
            arg_type = arg.relation_arg_type()
            prep = transform_state.relation_mgr.get(rel).decide_prep(arg_type)
            narg = arg.to_surface(transform_state, say_state, idiolect)
            preps_nargs.append([prep, narg])

        return SurfaceCommonNoun(
            possessor, self.selector, number, self.attributes, self.noun,
            preps_nargs)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        possessor = loader.load(d['possessor'])
        selector = Selector.load(d['selector'])
        number = loader.load(d['number'])
        attributes = d['attributes']
        noun = d['noun']

        rels_nargs = []
        for rel, arg in d['rels_nargs']:
            rel = Relation.from_str[rel]
            arg = loader.load(arg)
            rels_nargs.append((rel, arg))

        return DeepCommonNoun(possessor, selector, number, attributes, noun,
                              rels_nargs)
