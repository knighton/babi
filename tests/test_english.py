import json
import yaml

from panoptes.ling.glue.idiolect import Idiolect
from panoptes.ling.tree.arg_loader import ArgLoader
from panoptes.ling.tree.deep.sentence import DeepSentence
from panoptes.ling.english import English


def main():
    english = English()
    idiolect = Idiolect()
    loader = ArgLoader()
    fn = 'tests/english.yaml'
    ee = yaml.load(open(fn))
    for e in ee:
        text = e['text']
        structure = e['structure']
        dsen = DeepSentence.load(structure, loader)

        new_structure = dsen.dump()
        assert structure == new_structure

        new_text = english.text_from_dsen(dsen, idiolect)
        print text
        print new_text
        print


if __name__ == '__main__':
    main()
