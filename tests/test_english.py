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
        print
        print text
        structure = e['structure']
        dsen = DeepSentence.load(structure, loader)

        new_structure = dsen.dump()
        assert structure == new_structure

        new_text = english.text_from_dsen(dsen, idiolect)
        print new_text
        print
        assert text == new_text

        for new_dsen in english.each_dsen_from_text(unicode(text)):
            pass
            # print '*', json.dumps(new_dsen.dump(), sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
