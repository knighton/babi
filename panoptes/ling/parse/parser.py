from collections import defaultdict
from spacy.en import English
import sys

from panoptes.ling.parse.parse import Parse, Token


def truecase(tokens):
    ss = []
    for t in tokens:
        s = t.orth_
        if t.tag == 'NNP':
            pass
        elif t.tag == 'PRP' and s == 'I':
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
        tokens = self.nlp(text, parse=True)
        words = truecase(tokens)

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
        return [parse]
