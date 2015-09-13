from panoptes.ling.glue.relation import Relation, RelationArgType, \
    RelationManager


def main():
    m = RelationManager()

    rels_rats = [
        (Relation.AGENT, RelationArgType.THING),
        (Relation.TARGET, RelationArgType.THING),
    ]
    print m.decide_preps(rels_rats)


if __name__ == '__main__':
    main()
