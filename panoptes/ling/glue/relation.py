import yaml

from panoptes.etc.enum import enum


RELATION_TEXT = """
  - relation: IF
    position: OBLIQUE
    order: -100
    preps:
      - if FINITE_CLAUSE

  - relation: WHEN
    position: OBLIQUE
    order: -100
    preps:
      - when FINITE_CLAUSE

  - relation: AGENT
    position: SUBJECT
    order: 0
    preps:
      - by THING

  - relation: TARGET
    position: DIRECT_OBJECT
    order: 3
    preps:
      - X THING

  - relation: TO_RECIPIENT
    position: INDIRECT_OBJECT
    order: 1
    preps:
      - to THING

  - relation: FOR_RECIPIENT
    position: INDIRECT_OBJECT
    order: 1
    preps:
      - for THING

  - relation: BENEFICIARY
    position: OBLIQUE
    order: 5
    preps:
      - for THING

  - relation: TO_LOCATION
    position: OBLIQUE
    order: 5
    preps:
      - to THING

  - relation: OF
    position: OBLIQUE
    order: 10
    preps:
      - of THING

  - relation: ABOUT
    position: OBLIQUE
    order: 10
    preps:
      - about THING

  - relation: AT
    position: OBLIQUE
    order: 30
    preps:
      - at THING

  - relation: "ON"
    position: OBLIQUE
    order: 30
    preps:
      - on THING

  - relation: DURING
    position: OBLIQUE
    order: 50
    preps:
      - while FINITE_CLAUSE
      - while PREPLESS_GERUND
      - during THING

  - relation: BECAUSE
    position: OBLIQUE
    order: 100
    preps:
      - because of THING
      - because FINITE_CLAUSE
      - since FINITE_CLAUSE
"""


def make_relation_enum(relation_text):
    dd = yaml.load(relation_text)
    relations = map(lambda d: d['relation'], dd)
    enum_content = 'Relation = %s' % ' '.join(relations)
    return enum(enum_content)


Relation = make_relation_enum(RELATION_TEXT)


RelationPosition = enum("""
    RelationPosition = SUBJECT DIRECT_OBJECT INDIRECT_OBJECT OBLIQUE""")


def is_core_position(pos):
    return pos != RelationPosition.OBLIQUE


RelationArgType = enum('RelationArgType = FINITE_CLAUSE THING PREPLESS_GERUND')


class RelationInfo(object):
    def __init__(self, relation, position, order, preps_types):
        self.relation = relation
        assert Relation.is_valid(self.relation)

        self.position = position
        assert RelationPosition.is_valid(self.position)

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

        s = d['position']
        position = RelationPosition.from_str[s]

        order = d['order']

        preps_types = []
        for s in d['preps']:
            ss = s.split()
            prep = tuple(ss[:-1])
            if prep == ('X',):
                prep = None
            rat = RelationArgType.from_str[ss[-1]]
            preps_types.append((prep, rat))

        return RelationInfo(relation, position, order, preps_types)


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

        # The natural order of the core semantic roles when using active voice.
        #
        #   "I baked you a cake"
        #
        # If you deviate from this order, you must use a preposition.
        self.active_prepless_order = [
            RelationPosition.SUBJECT,
            RelationPosition.INDIRECT_OBJECT,
            RelationPosition.DIRECT_OBJECT,
        ]

        # Natural core order when in passive voice.
        #
        #   "You were baked a cake"
        self.passive_prepless_order = [
            RelationPosition.INDIRECT_OBJECT,
            RelationPosition.DIRECT_OBJECT,
        ]

    def decide_preps(self, rels_rats, subject_index):
        """
        list of (Relation, RelationArgType) -> list of (prep tuple or None).
        """
        # Verify that all rels are unique.
        rels = map(lambda (rel, rat): rel, rels_rats)
        assert len(rels) == len(set(rels))

        # Verify that core arg positions are unique (deep structure generation
        # error if this fails).
        core_positions = []
        for rel in rels:
            pos = self.relation2info[rel].position
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
            if not is_core_position(info.position):
                use_prep = True
            else:
                while True:
                    if index == len(preferred_core_order):
                        use_prep = True
                        break

                    if info.position == preferred_core_order[index]:
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

    def get(self, relation):
        return self.relation2info[relation]