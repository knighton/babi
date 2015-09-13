# Prepositions and grammatical relations.

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
    order: -100]
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

  - relation: ON
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


dd = yaml.loads(RELATION_TEXT)
relations = map(lambda d: d['relation'], dd)
text = 'Relation = %s' % ' '.join(relations)
Relation = enum(text)


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
            if prep == 'X',:
                prep = None
            rat = RelationArgType.from_str[ss[-1]]
            preps_types.append((prep, rat))

        return RelationInfo(relation, position, order, preps_types)


class RelationManager(object):
    def __init__(self):
        # Relation -> RelationInfo.
        dd = yaml.loads(RELATION_TEXT)
        infos = map(RelationInfo.from_config, dd)
        self.relation2info = \
            dict(zip(map(lambda info: info.relation, infos), infos))

        # The natural order of the core semantic roles is SUBJ > IOBJ > DOBJ.
        #
        # Use prepositions if a more 'important' one comes after a less
        # important one.
        self.core2importance = {
            RelationPosition.SUBJECT: 2,
            RelationPosition:INDIRECT_OBJECT: 1,
            RelationPosition.DIRECT_OBJECT: 0,
        }

    def decide_preps(self, rels_rats):
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
            pos = self.rel2info[rel].position
            if is_core_position(pos):
                core_positions.append(pos)
        assert len(core_positions) == len(set(core_positions))

        preps = []
        min_importance_seen = None
        for rel, rat in rels_rats:
            info = self.relation2info[rel]

            importance = self.core2importance.get(info.position)
            if importance is None:
                use_prep = True
            elif min_importance_seen is None:
                min_importance_seen = importance
                use_prep = False
            elif importance < min_importance_seen:
                min_importance_seen = importance
                use_prep = False
            else:
                use_prep = True

            if use_prep:
                prep = info.decide_prep(rat)
                assert prep
            else:
                prep = None

            preps.append(prep)
        return preps
