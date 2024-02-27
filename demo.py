from contextlib import contextmanager
import json
from time import sleep
from tqdm import trange
import yaml

from panoptes.ling.english import English
from panoptes.ling.glue.idiolect import Idiolect
from panoptes.ling.tree.arg_loader import ArgLoader
from panoptes.ling.tree.deep.sentence import DeepSentence
from panoptes.ling.verb.verb import DeepVerb

@contextmanager
def step(name):
    indent = ' ' * 4
    print()
    print(indent + name)
    print(indent + '-' * len(name))
    print()
    yield
    sleep(1.337)

dump = lambda x: json.dumps(x, indent=4, sort_keys=True)
dump = lambda x: yaml.safe_dump(x)

with step('Setup'):
    loader = ArgLoader()
    english = English()

with step('Verb'):
    obj = {
        'lemma': 'be',
        'polarity': {
            'tf': True,
            'is_contrary': False,
        },
        'tense': 'PRESENT',
        'aspect': {
            'is_perf': False,
            'is_prog': False,
        },
        'modality': {
            'flavor': 'IMPERATIVE',
            'is_cond': False,
        },
        'verb_form': 'FINITE',
        'is_pro_verb': False,
    }
    be = DeepVerb.load(obj)
    print(dump(be.dump()))

with step('Implied subject'):
    obj = {
        'type': 'PersonalPronoun',
        'declension': 'YALL',
        'ppcase': 'SUBJECT',
    }
    yall = loader.load(obj)
    print(dump(yall.dump()))

with step('Locative argument'):
    obj = {
        'type': 'DeepCommonNoun',
        'possessor': None,
        'selector': {
            'correlative': 'PROX',
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        },
        'number': None,
        'attributes': [],
        'noun': 'place',
        'rels_nargs': [],
    }
    here = loader.load(obj)
    print(dump(here.dump()))

with step('Temporal argument'):
    obj = {
        'type': 'DeepCommonNoun',
        'possessor': None,
        'selector': {
            'correlative': 'PROX',
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        },
        'number': None,
        'attributes': [],
        'noun': 'time',
        'rels_nargs': [],
    }
    now = loader.load(obj)
    print(dump(now.dump()))

with step('Content clause'):
    obj = {
        'type': 'DeepContentClause',
        'status': 'ACTUAL',
        'purpose': 'INFO',
        'is_intense': False,
        'verb': be.dump(),
        'adverbs': [],
        'rels_vargs': [
            ('AGENT', yall.dump()),
            ('PLACE', here.dump()),
            ('TIME', now.dump()),
        ],
        'subj_index': 0,
    }
    clause = loader.load(obj)
    print(dump(clause.dump()))

with step('Sentence'):
    obj = {
        'type': 'DeepSentence',
        'root': obj,
    }
    sentence = DeepSentence.load(obj, loader)
    print(dump(sentence.dump()))

with step('Idiolect'):
    obj = {
        'archaic_pro_adverbs': False,
        'contractions': True,
        'pedantic_plurals': False,
        'stranding': True,
        'split_infinitive': True,
        'subjunctive_were': True,
        'whom': False,
    }
    idiolect = Idiolect(**obj)
    print(dump(idiolect.__dict__))

with step('Result'):
    text = english.say(sentence, idiolect)
    print('$', text)  # "Be here now."
