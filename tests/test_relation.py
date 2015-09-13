from panoptes.ling.glue.relation import Relation, RelationArgType, \
    RelationManager


def main():
    THING = RelationArgType.THING

    m = RelationManager()

    # "I walked to the store".
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.TO_LOCATION, THING),
    ]
    assert m.decide_preps(rels_rats) == [None, ('to',)]

    # "I baked a cake".
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.TARGET, THING),
    ]
    assert m.decide_preps(rels_rats) == [None, None]

    # "The cake was baked by you."
    rels_rats = [
        (Relation.TARGET, THING),
        (Relation.AGENT, THING),
    ]
    assert m.decide_preps(rels_rats) == [None, ('by',)]

    # "The cake was baked for you."
    rels_rats = [
        (Relation.TARGET, THING),
        (Relation.FOR_RECIPIENT, THING),
    ]
    assert m.decide_preps(rels_rats) == [None, ('for',)]

    # "I baked you a cake.
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.FOR_RECIPIENT, THING),
        (Relation.TARGET, THING),
    ]
    assert m.decide_preps(rels_rats) == [None, None, None]

    # "I baked a cake for you."
    rels_rats = [
        (Relation.AGENT, THING),
        (Relation.TARGET, THING),
        (Relation.FOR_RECIPIENT, THING),
    ]
    assert m.decide_preps(rels_rats) == [None, None, ('for',)]

    # "For you I baked a cake."
    rels_rats = [
        (Relation.FOR_RECIPIENT, THING),
        (Relation.AGENT, THING),
        (Relation.TARGET, THING),
    ]
    assert m.decide_preps(rels_rats) == [('for',), None, None]

    # "For you a cake was baked by me."
    rels_rats = [
        (Relation.FOR_RECIPIENT, THING),
        (Relation.TARGET, THING),
        (Relation.AGENT, THING),
    ]
    assert m.decide_preps(rels_rats) == [('for',), None, ('by',)]


if __name__ == '__main__':
    main()
