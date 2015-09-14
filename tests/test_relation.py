from panoptes.ling.glue.relation import Relation, RelationArgType, \
    RelationManager


THING = RelationArgType.THING


def two_core_args(m):
    # "I baked a cake".
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.TARGET, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, None]

    # "The cake was baked by you."
    rels_rats = [
        (Relation.TARGET, THING),
        (Relation.AGENT, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, ('by',)]

    # "The cake was baked for you."
    rels_rats = [
        (Relation.TARGET, THING),
        (Relation.FOR_RECIPIENT, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, ('for',)]


def three_core_args(m):
    # "I baked you a cake.
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.FOR_RECIPIENT, THING),
        (Relation.TARGET, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, None, None]

    # "I baked a cake for you."
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.TARGET, THING),
        (Relation.FOR_RECIPIENT, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, None, ('for',)]

    # "You were baked by me a cake."
    rels_rats = [
        (Relation.FOR_RECIPIENT, THING),
        (Relation.AGENT, THING),
        (Relation.TARGET, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, ('by',), None]

    # "You were baked a cake by me."
    rels_rats = [
        (Relation.FOR_RECIPIENT, THING),
        (Relation.TARGET, THING),
        (Relation.AGENT, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, None, ('by',)]

    # "A cake was baked by me for you."
    rels_rats = [
        (Relation.TARGET, THING),
        (Relation.AGENT, THING),
        (Relation.FOR_RECIPIENT, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, ('by',), ('for',)]

    # "A cake was baked for you by me."
    rels_rats = [
        (Relation.TARGET, THING),
        (Relation.FOR_RECIPIENT, THING),
        (Relation.AGENT, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, ('for',), ('by',)]


def misc(m):
    # "I walked to the store".
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.TO_LOCATION, THING),
    ]
    subj = 0
    assert m.decide_preps(rels_rats, subj) == [None, ('to',)]

    # "Because I like you, I walk to your house during the sunrise."
    rels_cats = [
        (Relation.BECAUSE, RelationArgType.FINITE_CLAUSE),
        (Relation.AGENT, THING),
        (Relation.TO_LOCATION, THING),
        (Relation.DURING, THING),
    ]
    subj = 1
    assert m.decide_preps(rels_rats, subj) == \
        [('because',), None, ('to',), ('during',)]

    # "Because I like you, I walk to your house while the sun rises."
    rels_cats = [
        (Relation.BECAUSE, RelationArgType.FINITE_CLAUSE),
        (Relation.AGENT, THING),
        (Relation.TO_LOCATION, THING),
        (Relation.DURING, RelationArgType.FINITE_CLAUSE),
    ]
    subj = 1
    assert m.decide_preps(rels_rats, subj) == \
        [('because',), None, ('to',), ('while',)]


def main():
    m = RelationManager()
    two_core_args(m)
    three_core_args(m)
    misc(m)


if __name__ == '__main__':
    main()
