### panoptes (solution for [fb.ai/babi](https://fb.ai/babi) 20 QA tasks)

#### 1. Mind

##### Organization

```
panoptes/mind/
├── idea
│   ├── base.py
│   ├── clause.py
    def __init__(self, status=Status.ACTUAL, purpose=Purpose.INFO,
                 is_intense=False, verb=None, adverbs=None, rel2xxx=None):
│   ├── comparative.py
    def __init__(self, polarity, adjective, than_x):

│   ├── direction.py
│   ├── __init__.py
│   ├── noun.py
    def __init__(self, query=None, name=None, gender=None,
                 is_animate=None, attributes=None, kind=None,
                 rel2xxx=None, carrying=None):
│   ├── reverb.py
│   └── time.py
├── __init__.py
├── know
│   ├── cause_and_effect.yaml
│   ├── cause_effect.py
│   ├── graph.py
│   ├── __init__.py
│   ├── location.py
│   ├── memory.py
│   └── user.py
├── mind.py
└── verb
    ├── base.py
    ├── be.py
    ├── carry.py
    ├── fear.py
    ├── fit.py
    ├── give.py
    ├── go.py
    ├── __init__.py
    └── manager.py
```

##### Flow

```
        checkpoint = self.memory.make_checkpoint()

        from_xx = list(map(self.user_mgr.get, from_uids))
        to_xx = list(map(self.user_mgr.get, to_uids))
        x = self.memory.decode_dsen(dsen, from_xx, to_xx)

        if x is None:
            self.memory.load_checkpoint(checkpoint)
            return None

        c = self.memory.ideas[x]
        r = self.semantics_mgr.handle(c)

        if not r:
            self.memory.load_checkpoint(checkpoint)
            return None

        return r
```

#### 2. Language

##### Recognize

`Text` >> parse >> `Parse` >> recog >> `S-Structure` >> unfront >> `D-Structure` >> resolve >> `Memory`

##### Generate

`Text` << contract << `Tokens` << render << `S-Structure` << front << `D-Structure` << refer << `Memory`

#### 3. Python example ("headless" mode)

##### Setup

```
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

loader = ArgLoader()
english = English()
```

##### Get the verb
```
conf = {
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
be = DeepVerb.load(conf)
print(dump(be))
```

##### Get the implied subject
```
conf = {
    'type': 'PersonalPronoun',
    'declension': 'YALL',
    'ppcase': 'SUBJECT',
}
yall = loader.load(conf)
print(dump(yall))
```

##### Get a locative verb argument
```
conf = {
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
here = loader.load(conf)
print(dump(here))
```

##### Get a temporal verb argument
```
conf = {
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
now = loader.load(conf)
print(dump(now))
```

##### Now connect them together into a content clause
```
conf = {
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
clause = loader.load(conf)
print(dump(clause))
```

##### That clause is our sentence
```
conf = {
    'type': 'DeepSentence',
    'root': conf,
}
sentence = DeepSentence.load(conf, loader)
print(dump(sentence))
```

##### Configure how it will be said
```
conf = {
    'archaic_pro_adverbs': False,
    'contractions': True,
    'pedantic_plurals': False,
    'stranding': True,
    'split_infinitive': True,
    'subjunctive_were': True,
    'whom': False,
}
idiolect = Idiolect(**conf)
dump(idiolect.__dict__)
```

##### Generate
```english = English()
text = english.say(sentence, idiolect)
print('$', text)  # "Be here now."
```
