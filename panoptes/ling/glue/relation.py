from collections import defaultdict
import yaml

from panoptes.etc.enum import enum
from panoptes.ling.glue.magic_token import PLACE_PREP, TIME_PREP, WAY_PREP


RELATION_TEXT = """
  - relation: IF
    core: OBLIQUE
    order: -100
    preps:
      - if FINITE_CLAUSE

  - relation: WHEN
    core: OBLIQUE
    order: -100
    preps:
      - when FINITE_CLAUSE

  - relation: AGENT
    core: NOMINATIVE
    order: 0
    preps:
      - by INERT

  - relation: TO_RECIPIENT
    core: DATIVE
    order: 1
    preps:
      - to INERT

  - relation: FOR_RECIPIENT
    core: DATIVE
    order: 1
    preps:
      - for INERT

  - relation: TARGET
    core: ACCUSATIVE
    order: 3
    preps:
      - X INERT

  - relation: BENEFICIARY
    core: OBLIQUE
    order: 5
    preps:
      - for INERT

  - relation: TO_LOCATION
    core: OBLIQUE
    order: 5
    preps:
      - to INERT

  - relation: PLACE
    core: OBLIQUE
    order: 5
    preps:
      - <PLACE_PREP> INERT

  - relation: TIME
    core: OBLIQUE
    order: 10
    preps:
      - <TIME_PREP> INERT

  - relation: WAY
    core: OBLIQUE
    order: 10
    preps:
      - <WAY_PREP> INERT

  - relation: OF
    core: OBLIQUE
    order: 10
    preps:
      - of INERT

  - relation: ABOUT
    core: OBLIQUE
    order: 10
    preps:
      - about INERT

  - relation: TO
    core: OBLIQUE
    order: 30
    preps:
      - to INERT

  - relation: AT
    core: OBLIQUE
    order: 30
    preps:
      - at INERT

  - relation: "ON"
    core: OBLIQUE
    order: 30
    preps:
      - on INERT

  - relation: IN
    core: OBLIQUE
    order: 30
    preps:
      - in INERT

  - relation: INSIDE
    core: OBLIQUE
    order: 30
    preps:
      - inside INERT

  - relation: BELOW
    core: OBLIQUE
    order: 30
    preps:
      - below INERT
      - under INERT

  - relation: ABOVE
    core: OBLIQUE
    order: 30
    preps:
      - over INERT
      - above INERT

  - relation: FROM_SOURCE
    core: OBLIQUE
    order: 30
    preps:
      - from INERT

  - relation: DURING
    core: OBLIQUE
    order: 50
    preps:
      - while FINITE_CLAUSE
      - while PREPLESS_GERUND
      - during INERT

  - relation: BEFORE
    core: OBLIQUE
    order: 50
    preps:
      - before FINITE_CLAUSE
      - before INERT

  - relation: AFTER
    core: OBLIQUE
    order: 50
    preps:
      - after FINITE_CLAUSE
      - after INERT

  - relation: BECAUSE
    core: OBLIQUE
    order: 100
    preps:
      - because of INERT
      - because FINITE_CLAUSE
      - since FINITE_CLAUSE
"""

RELATION_TEXT = RELATION_TEXT.replace('<PLACE_PREP>', PLACE_PREP)
RELATION_TEXT = RELATION_TEXT.replace('<TIME_PREP>', TIME_PREP)
RELATION_TEXT = RELATION_TEXT.replace('<WAY_PREP>', WAY_PREP)


def make_relation_enum(relation_text):
    dd = yaml.load(relation_text)
    relations = map(lambda d: d['relation'], dd)
    enum_content = 'Relation = %s' % ' '.join(relations)
    return enum(enum_content)


Relation = make_relation_enum(RELATION_TEXT)


RelationPosition = enum("""
    RelationPosition = NOMINATIVE DATIVE ACCUSATIVE OBLIQUE""")


def is_core_position(pos):
    return pos != RelationPosition.OBLIQUE


# INERT is most args, and non-finite clauses.
# FINITE_CLAUSE is finite clauses.
RelationArgType = enum('RelationArgType = INERT FINITE_CLAUSE PREPLESS_GERUND')


class RelationInfo(object):
    def __init__(self, relation, core, order, preps_types):
        self.relation = relation
        assert Relation.is_valid(self.relation)

        self.core = core
        assert RelationPosition.is_valid(self.core)

        self.order = order
        assert isinstance(self.order, int)

        self.preps_types = preps_types
        assert isinstance(self.preps_types, list)
        for prep, rat in self.preps_types:
            if prep is not None:
                assert prep
                assert isinstance(prep, tuple)
            assert RelationArgType.is_valid(rat)

    def decide_prep(self, have_arg_type):
        for prep, want_arg_type in self.preps_types:
            if have_arg_type == want_arg_type:
                return prep

        return None

    @staticmethod
    def from_config(d):
        s = d['relation']
        relation = Relation.from_str[s]

        s = d['core']
        core = RelationPosition.from_str[s]

        order = d['order']

        preps_types = []
        for s in d['preps']:
            ss = s.split()
            prep = tuple(ss[:-1])
            if prep == ('X',):
                prep = None
            rat = RelationArgType.from_str[ss[-1]]
            preps_types.append((prep, rat))

        return RelationInfo(relation, core, order, preps_types)


class RelationManager(object):
    """
    Manages knowledge about grammatical relations and prepositions.
    """

    def __init__(self):
        # Relation -> RelationInfo.
        dd = yaml.load(RELATION_TEXT)
        infos = map(RelationInfo.from_config, dd)
        self.relation2info = \
            dict(zip(map(lambda info: info.relation, infos), infos))

        # The natural order of the core (non-oblique -- without a preposition)
        # semantic roles when using active voice.
        #
        #   "I baked you a cake"
        #
        # If you deviate from this order, you must use a preposition.
        self.active_prepless_order = [
            RelationPosition.NOMINATIVE,
            RelationPosition.DATIVE,
            RelationPosition.ACCUSATIVE,
        ]

        # Natural core argument order when in passive voice.
        #
        #   "You were baked a cake"
        self.passive_prepless_order = [
            RelationPosition.DATIVE,
            RelationPosition.ACCUSATIVE,
        ]

        # (prep, arg type) -> possible Relations.
        self.prep_rat2relations = defaultdict(list)
        for relation, info in self.relation2info.iteritems():
            for prep, arg_type in info.preps_types:
                self.prep_rat2relations[(prep, arg_type)].append(relation)

        # (is active voice, prepless arg count) -> Relation per prepless arg.
        self.isactive_numprepless2positions = {
            (True, 1): [
                RelationPosition.NOMINATIVE,
            ],
            (True, 2): [
                RelationPosition.NOMINATIVE,
                RelationPosition.ACCUSATIVE,
            ],
            (True, 3): [
                RelationPosition.NOMINATIVE,
                RelationPosition.DATIVE,
                RelationPosition.ACCUSATIVE,
            ],
            (False, 1): [
                RelationPosition.ACCUSATIVE,
            ],
            (False, 2): [
                RelationPosition.DATIVE,
                RelationPosition.ACCUSATIVE,
            ],
        }

        # RelationPosition -> list of possible Relations.
        self.core2relations = defaultdict(list)
        for relation, info in self.relation2info.iteritems():
            self.core2relations[info.core].append(relation)

    def decide_preps(self, rels_rats, subject_index):
        """
        list of (Relation, RelationArgType) -> list of (prep tuple or None).

        Used in deep structure -> surface structure.
        """
        # Verify that all rels are unique.
        rels = map(lambda (rel, rat): rel, rels_rats)
        assert len(rels) == len(set(rels))

        # Verify that core arg positions are unique (deep structure generation
        # error if this fails).
        core_positions = []
        for rel in rels:
            pos = self.relation2info[rel].core
            if is_core_position(pos):
                core_positions.append(pos)
        assert len(core_positions) == len(set(core_positions))

        # Prefer one ordering if active voice, a different one if passive voice.
        if rels_rats[subject_index][0] == Relation.AGENT:
            preferred_core_order = self.active_prepless_order
        else:
            preferred_core_order = self.passive_prepless_order

        # Collect each prep.
        preps = []
        index = 0
        for rel, arg_type in rels_rats:
            info = self.relation2info[rel]
            if not is_core_position(info.core):
                use_prep = True
            else:
                while True:
                    if index == len(preferred_core_order):
                        use_prep = True
                        break

                    if info.core == preferred_core_order[index]:
                        use_prep = False
                        break

                    index += 1

            if use_prep:
                prep = info.decide_prep(arg_type)

                # Allow the iffy construction "you were baked by me a cake" for
                # the sake of having all the core argument order permutations.
                # Check everything else.
                if rel != Relation.TARGET:
                    assert prep
            else:
                prep = None

            preps.append(prep)
        return preps

    def decode_prep_type(self, prep, arg_type):
        return self.prep_rat2relations[(prep, arg_type)]

    def relations_per_prepless_varg(self, num_prepless, is_active_voice):
        """
        number prepless args, active -> Relation options per prepless arg
        """
        key = (is_active_voice, num_prepless)
        cores = self.isactive_numprepless2positions.get(key, None)
        if not cores:
            return None
        return map(lambda core: self.core2relations[core], cores)

    def decide_clause_relation_options(self, preps_rats, is_active_voice):
        """
        list of (prep tuple, RelationArgType) -> Relation options per arg

        Used in surface structure -> deep structure.
        """
        options_per_arg = [None] * len(preps_rats)

        prepless = []
        for i, (prep, arg_type) in enumerate(preps_rats):
            if prep:
                options_per_arg[i] = self.decode_prep_type(prep, arg_type)
            else:
                prepless.append(i)

        if not prepless:
            return options_per_arg

        relations_per_prepless = self.relations_per_prepless_varg(
            len(prepless), is_active_voice)
        if not relations_per_prepless:
            return None

        for x, relations in zip(prepless, relations_per_prepless):
            options_per_arg[x] = relations

        options_per_arg = filter(lambda rr: len(set(rr)) == len(rr),
                                 options_per_arg)

        return options_per_arg

    def decide_noun_phrase_relation_options(self, preps_rats):
        options_per_arg = []
        for prep, rat in preps_rats:
            rels = self.decode_prep_type(prep, rat)
            if not rels:
                print 'Unknown preposition + arg type:', prep, \
                    RelationArgType.to_str[rat]
                return None
            options_per_arg.append(rels)

        options_per_arg = filter(lambda rr: len(set(rr)) == len(rr),
                                 options_per_arg)

        return options_per_arg

    def get(self, relation):
        return self.relation2info[relation]
