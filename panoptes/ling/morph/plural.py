import yaml


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


def load_normal_rules(f):
    rules = []
    with open(f) as f:
        for line in f:
            sing_suffix, plur_suffix = line.split()
            rule = Rule(sing_suffix, plur_suffix, None, False)
            rules.append(rule)
    return rules


def load_nonsuffixable_rules(f):
    return load_normal_rules(f)


def load_capitalized_rules(f):
    return load_normal_rules(f)


class PluralManager(object):
    @staticmethod
    def from_files(capitalized_f, categories_f, nonsuffixable_f, rules_f):
        cat2sings = load_categories(categories_f)
        normal_rules = load_normal_rules(rules_f)
        nonsuffixable_rules = load_nonsuffixable_rules(nonsuffixable_f)
        capitalized_rules = load_capitalized_rules(capitalized_f)
        return PluralManager(cat2sings, normal_rules, nonsuffixable_rules,
                             capitalized_rules)

    def __init__(self, cat2sings, normal_rules, nonsuffixable_rules,
                 capitalized_rules):
        for r in normal_rules + nonsuffixable_rules + capitalized_rules:
            if r.category_only:
                for sing in cat2sings[r.category_only]:
                    assert sing.endswith(r.sing_suffix)
