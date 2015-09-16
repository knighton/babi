from panoptes.etc.enum import enum
from panoptes.ling.verb.annotation import annotate_as_aux


class ContractionTableParser(object):
    """
    Parses contraction tables for bigram contractor init.
    """

    def __init__(self):
        self.fake2real = {
            'AUX_HAVE': annotate_as_aux('have'),
            'AUX_HAS': annotate_as_aux('has'),
            'AUX_HAD': annotate_as_aux('had'),
        }

    def fix(self, s):
        return self.fake2real.get(s, s)

    def parse_table(self, text):
        sss = map(lambda line: line.split(), text.strip().split('\n'))

        n = len(sss[0])
        for ss in sss[1:]:
            assert len(ss) == n + 1

        rows = map(self.fix, map(lambda ss: s[0], sss[1:]))
        cols = map(self.fix, sss[0])

        rr = set()
        for i in xrange(len(sss) - 1):
            for j in xrange(n):
                row = rows[i]
                col = cols[j]
                s = sss[i + 1][j + 1]
                if s == '-':
                    continue
                elif s == '!':
                    continue
                elif s == 'x':
                    value = True
                    rr.add((row, col))
        return rr

    def parse_dict(self, text):
        r = {}
        sss = map(lambda line: line.split(), text.strip().split('\n'))
        for ss in sss:
            key, value = map(self.fix, ss)
            r[key] = value
        return r


class EndsWithSSoundDetector(object):
    """
    Detects whether a token ends in something vaguely resembling an "s" sound.
    """

    def __init__(self):
        self.regexes = map(re.compile, [
            '[sxz]$',
            '[cszt]h$',
            '[iy][sz]ed?$',
            '[aeiourl][cs]e$',
            '[aeiourl]the$'
        ])

    def detect(self, s):
        for r in self.regexes:
            if r.search(s):
                return True
        return False


Contract = enum('Contract = IF_NOT_S_SOUND ALWAYS')


class BigramContractionManager(object):
    def __init__(self, bigram2exception, bigrams_to_contract, last2contract,
                 last2contraction):
        # Exceptions (maps bigrams to their weird contractions).
        self.bigram2exception = bigram2exception

        # Set of bigrams to contract.
        self.bigrams_to_contract = bigrams_to_contract

        # Contraction behavior given last word in a bigram.
        self.last2contract = last2contract

        # How to contract the last word of a bigram.
        self.last2contraction = last2contraction

        for _, last in self.bigrams_to_contract:
            assert last in self.last2contraction

        # Whether a word vaguely ends with an "s" sound.
        self.ends_with_s_sound = EndsWithSSoundDetector()

    def normal_contraction(self, first, second):
        return remove_verb_annotations(first) + self.last2contraction[last]

    def contract(self, first, last, use_contractions):
        bigram = (first, last)

        # Exceptions (its, won't).
        r = self.bigram2exception.get(bigram)
        if r:
            return r

        # Common cases (it's, you're, should've, didn't).
        if bigram in self.bigrams_to_contract:
            return self.normal_contraction(first, last)

        # Verbs that are said like suffixes (has, is, will, would).
        behavior = self.last2contract.get(last)
        if behavior:
            if behavior == Contract.IF_NOT_S_SOUND:
                if self.ends_with_s_sound.detect(first):
                    return self.normal_contraction(first, last)
            elif behavior == Contract.ALWAYS:
                return self.normal_contraction(first, last)
            else:
                assert False

        # Don't contract it.
        return None

    @staticmethod
    def default():
        p = ContractionTableParser()

        pairs = set()

        pairs.update(p.parse_table("""
                 am are is
            I    x  -   -
            you  -  x   -
            he   -  -   x
            she  -  -   x
            it   -  -   x
            we   -  x   -
            they -  x   -
        """))

        pairs.update(p.parse_table("""
                 AUX_HAVE AUX_HAS AUX_HAD
            I    x        -       x
            you  x        -       x
            he   -        x       x
            she  -        x       x
            it   -        x       x
            we   x        -       x
            they x        -       x
        """))

        pairs.update(p.parse_table("""
                 will would
            I    x    x
            you  x    x
            he   x    x
            she  x    x
            it   x    x
            we   x    x
            they x    x
        """))

        pairs.update(p.parse_table("""
                  is AUX_HAVE did
            this  -  -        -
            that  x  -        -
            here  x  -        -
            there x  -        -
            what  x  x        -
            where x  x        x
            when  x  -        -
            why   x  -        x
            how   x  x        x
        """))

        pairs.update(p.parse_table("""
                     not
            am       -
            are      x
            is       x
            was      x
            were     x
            AUX_HAVE x
            AUX_HAS  x
            AUX_HAD  x
            do       x
            does     x
            did      x
        """))

        pairs.update(p.parse_table("""
                   AUX_HAVE not
            can    -        x
            could  x        x
            may    -        -
            might  x        -
            must   x        x
            should x        x
            would  x        x
            will   -        !
        """))

        bigrams_to_contract = pairs

        bigram2exception = {
            ('will', 'not'): "won't",
            ('it', POSSESSIVE_MARK): 'its',
        }

        last2contract = {
            annotate_as_aux('has'): Contract.IF_NOT_S_SOUND,
            'is': Contract.IF_NOT_S_SOUND,
            'will': Contract.ALWAYS,
            'would': Contract.ALWAYS,
        }

        last2contraction = p.parse_dict("""
            am       'm
            are      're
            is       's
            AUX_HAVE 've
            AUX_HAS  's
            AUX_HAD  'd
            did      'd
            not      n't
            will     'll
            would    'd
        """)

        return BigramContractionManager(
            bigram2exception, bigrams_to_contract, last2contract,
            last2contraction)


class ContractionManager(object):
    def __init__(self):
        self.bigram_mgr = BigramContractionManager.default()

    def contract(self, tokens, use_contractions):
        XXX
