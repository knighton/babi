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


class BigramContractionManager(object):
    def __init__(self):
        p = ContractionTableParser()

        pers_be = p.parse_table("""
                 am are is
            I    x  -   -
            you  -  x   -
            he   -  -   x
            she  -  -   x
            it   -  -   x
            we   -  x   -
            they -  x   -
        """) 

        pers_have = p.parse_table("""
                 AUX_HAVE AUX_HAS AUX_HAD
            I    x        -       x
            you  x        -       x
            he   -        x       x
            she  -        x       x
            it   -        x       x
            we   x        -       x
            they x        -       x
        """)

        pers_modal = p.parse_table("""
                 will would
            I    x    x
            you  x    x
            he   x    x
            she  x    x
            it   x    x
            we   x    x
            they x    x
        """)

        shortcut = p.parse_table("""
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
        """)

        verb_not = p.parse_table("""
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
        """)

        modal = p.parse_table("""
                   AUX_HAVE not
            can    -        x
            could  x        x
            may    -        -
            might  x        -
            must   x        x
            should x        x
            would  x        x
            will   -        !
        """)


class ContractionManager(object):
    def __init__(self):
        self.bigrams = BigramContractionManager()

    def contract(self, tokens, use_contractions):
        XXX
