from collections import defaultdict
from spacy.en import English
import sys

from panoptes.ling.parse.parse import Parse, Token


def truecase(tokens):
    ss = []
    for t in tokens:
        s = t.orth_
        if t.tag_ == 'NNP':
            if s.islower():
                s = s.title()
        elif t.tag_ == 'PRP' and s == 'I':
            pass
        else:
            s = s.lower()
        ss.append(s)
    return ss


class Parser(object):
    def __init__(self):
        print 'Initializing spacy...',
        sys.stdout.flush()
        self.nlp = English()
        print 'done'

    def parse(self, text):
        # I'm deciding "afraid" is a passive verb.  Have it parse as such.
        text = text.replace('afraid of', 'seen by')
        text = text.replace('afraid', 'seen')

        # Fred gets parsed by spacy as VBN.  Replace with a unique name.
        text = text.replace(' Fred ', ' Jameson ')
        text = text.replace(' fred ', ' jameson ')

        # It thinks Emily is an adverb.
        text = text.replace(' emily ', ' Elliot ')
        text = text.replace(' Emily ', ' Elliot ')

        # It thinks Winona is an adjective.
        text = text.replace(' winona ', ' Ashley ')
        text = text.replace(' Winona ', ' Ashley ')

        # And that gertrude is a common noun.
        text = text.replace(' gertrude ', ' Gertrude ')

        # spaCy doesn't like "following" used as a preposition, so we use a
        # similar word instead.  Oh well.
        text = text.replace('Following', 'After')

        tokens = self.nlp(text, parse=True)
        words = truecase(tokens)
        words = map(lambda s: 'Fred' if s == 'Jameson' else s, words)
        words = map(lambda s: 'thwacked' if s == 'seen' else s, words)
        words = map(lambda s: 'Emily' if s == 'Elliot' else s, words)
        words = map(lambda s: 'Winona' if s == 'Ashley' else s, words)

        x2dep_x = {}
        x2deps_xx = defaultdict(list)
        for i, t in enumerate(tokens):
            if t.head is t:
                head_x = None
            else:
                head_x = t.head.i
            x2dep_x[i] = (t.dep_, head_x)
            x2deps_xx[head_x].append((t.dep_, t.i))

        tt = []
        for i, token in enumerate(tokens):
            t = Token(i, words[i], token.tag_, x2dep_x[i], x2deps_xx[i])
            tt.append(t)

        for t in tt:
            dep, x = t.up
            if x is not None:
                t.up = (dep, tt[x])
            new_downs = []
            for dep, x in t.downs:
                new_downs.append((dep, tt[x]))
            t.downs = new_downs

        root = tt[x2deps_xx[None][0][1]]
        parse = Parse(tt, root)
        return filter(bool, map(lambda p: p.fixed(), [parse]))
