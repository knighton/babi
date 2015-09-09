from collections import defaultdict
import yaml

from etc.suffix_fanout_map import SuffixFanoutMap


def remove_then_append(s, remove, append):
    if remove:
        assert s.endswith(remove)
        s = s[:-len(remove)]
    s += append
    return s


class Rule(object):
    """
    A single pluralization rule.
    """

    def __init__(self, sing_suffix, plur_suffix, category_only, is_pedantic):
        self.sing_suffix = sing_suffix
        assert isinstance(self.sing_suffix, str)

        self.plur_suffix = plur_suffix
        assert isinstance(self.plur_suffix, str)

        self.category_only = category_only
        if self.category_only:
            assert isinstance(self.category_only, str)

        self.is_pedantic = is_pedantic
        assert isinstance(self.is_pedantic, bool)

    def sing_from_plur(self, plur):
        return remove_then_append(plur, self.plur_suffix, self.sing_suffix)

    def plur_from_sing(self, sing):
        return remove_then_append(sing, self.sing_suffix, self.plur_suffix)


def load_categories(f):
    cat2sings = {}
    dd = yaml.load(open(f))
    for d in dd:
        name = d['name']
        words = d['words']
        cat2sings[name] = words
    return cat2sings


def load_rules(f):
    ss = []
    with open(f) as f:
        for line in f:
            x = line.find('#')
            s = line[:x].strip()
            if not s:
                continue
            ss.append(s)

    rules = []
    for s in ss:
        sing_suffix, plur_suffix, pedantic, cat = s.split()

        if sing_suffix == '-':
            sing_suffix = ''

        if plur_suffix == '-':
            plur_suffix = ''

        if pedantic == 'x':
            pedantic = True
        elif pedantic == '-':
            pedantic = False
        else:
            assert False

        if cat == '-':
            cat = None

        rule = Rule(sing_suffix, plur_suffix, cat, pedantic)
        rules.append(rule)

    return rules


def load_sing2plur(f):
    sing2plur = {}
    with open(f) as f:
        for line in f:
            sing, plur = line.split()
            assert sing not in sing2plur
            sing2plur[sing] = plur
    return sing2plur


def singular_suffixes_from_rule(rule, cat2sings):
    if rule.category_only:
        return cat2sings[rule.category_only]
    else:
        return [rule.sing_suffix]


def plural_suffixes_from_rule(rule, cat2sings):
    if rule.category_only:
        return map(rule.plur_from_sing, cat2sings[rule.category_only])
    else:
        return [rule.plur_suffix]


def each_suffix_shortest_first(s):
    for i in xrange(len(s) + 1):
        yield s[len(s) - i:]


class PluralManager(object):
    @staticmethod
    def from_files(category_f, rule_f, nonsuffixable_f, capitalized_f):
        cat2sings = load_categories(category_f)
        rules = load_rules(rule_f)
        nonsuffixable_sing2plur = load_sing2plur(nonsuffixable_f)
        capitalized_sing2plur = load_sing2plur(capitalized_f)
        return PluralManager(cat2sings, rules, nonsuffixable_sing2plur,
                             capitalized_sing2plur)

    def __init__(self, cat2sings, rules, nonsuffixable_sing2plur,
                 capitalized_sing2plur):
        sings_set = set()
        for r in rules:
            if r.category_only:
                for sing in cat2sings[r.category_only]:
                    assert sing.endswith(r.sing_suffix)
                    assert sing not in sings_set
                    sings_set.add(sing)

        sing2x = {}
        sing2x_pedantic_ok = {}
        plur2xx = defaultdict(list)
        plur2xx_pedantic_ok = defaultdict(list)
        for i, rule in enumerate(rules):
            for s in singular_suffixes_from_rule(rule, cat2sings):
                assert s not in sing2x_pedantic_ok
                sing2x_pedantic_ok[s] = i
                if not rule.is_pedantic:
                    sing2x[s] = i
            for s in plural_suffixes_from_rule(rule, cat2sings):
                plur2xx_pedantic_ok[s].append(i)
                if not rule.is_pedantic:
                    plur2xx[s].append(i)

        self.sing2x = SuffixFanoutMap(sing2x, None, min)
        self.sing2x_pedantic_ok = SuffixFanoutMap(sing2x_pedantic_ok, None, min)
        self.plur2xx = SuffixFanoutMap(plur2xx, [], min)
        self.plur2xx_pedantic_ok = SuffixFanoutMap(plur2xx_pedantic_ok, [], min)

        self.rules = rules
        self.nonsuffixable_sing2plur = nonsuffixable_sing2plur
        self.capitalized_sing2plur = capitalized_sing2plur

    def name_to_plural(self, s):
        for sing_suffix in each_suffix_shortest_first(s):
            plur_suffix = self.sing2plur_capitalized.get(sing_suffix)
            if not plur_suffix:
                continue
            return remove_then_append(s, sing_suffix, plur_suffix)
        return None

    def to_plural(self, s, is_pedantic_ok=False):
        """
        singular, pedantic ok -> plural
        """
        assert isinstance(s, basestring)
        assert s
        assert isinstance(is_pedantic_ok, bool)

        # Names.
        if s[0].isupper():
            return self.name_to_plural(s)

        # Special non-suffixable words.
        #
        # If we hit this, it is all you need (eg, ox -> oxen).
        r = self.nonsuffixable_sing2plur.get(s)
        if r:
            return r

        # Everything else.
        if is_pedantic_ok:
            a = self.sing2x_pedantic_ok
        else:
            a = self.sing2x
        x = a.get(s)
        return self.rules[x].plur_from_sing(s)

    def name_to_singular(self, s):
        for plur_suffix in each_suffix_shortest_first(s):
            sing_suffix = self.plur2sing_capitalized.get(plur_suffix)
            if not sing_suffix:
                continue
            return remove_then_append(s, plur_suffix, sing_suffix)
        return None

    def to_singular(self, s, is_pedantic_ok=False):
        """
        plural, pedantic ok -> list of possible singulars
        """
        assert isinstance(s, basestring)
        assert s
        assert isinstance(is_pedantic_ok, bool)

        # Names.
        if s[0].isupper():
            return [self.name_to_singular(s)]

        # Special non-suffixable words.
        r = self.nonsuffixable_plur2sing.get(s)
        if r:
            return [r]

        # Everything else.
        if is_pedantic_ok:
            a = self.plur2xx_pedantic_ok
        else:
            a = self.plur2xx
        rr = []
        for x in a.get(s):
            r = self.rules[x].sing_from_plur(s)
            rr.append(r)
        return rr

    def identify(self, word):
        """
        word -> list of (singular form, is plural)
        """
        ss = self.to_singular(word, is_pedantic_ok=True)

        # If we cannot make it singular, it must already be singular.
        if not ss:
            return [(word, False)]

        # Else if singular and plural forms are the same, return both.
        if ss == [word]:
            return [(word, False), (word, True)]

        # It has a singular form(s), so it certainly is a plural (and may or
        # may not be its own singular form as well).
        rr = map(lambda s: (s, True), ss)

        same = False
        for s in ss:
            if s == word:
                same = True
                break
        if same:
            rr.append((s, False))

        return rr
