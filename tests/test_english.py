import yaml

from panoptes.ling.tree.deep.sentence import DeepSentence
from panoptes.ling.tree.arg_loader import ArgLoader


def main():
    loader = ArgLoader()
    fn = 'tests/english.yaml'
    ee = yaml.load(open(fn))
    for e in ee:
        text = e['text']
        structure = e['structure']
        dsen = DeepSentence.load(structure, loader)


if __name__ == '__main__':
    main()
