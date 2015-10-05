from collections import defaultdict
import re
import yaml

from panoptes.etc.dicts import v2k_from_k2v
from panoptes.etc.enum import enum


ComparativeDegree = enum('ComparativeDegree = BASE COMP SUPER')


ComparativePolarity = enum('ComparativePolarity = POS NEG')


class ComparativeManager(object):
    def __init__(self, syllable_counter, exception_triples, base_is_er_est,
                 erable, not_erable):
        self.syllable_counter = syllable_counter

        self.exception_bases = set(map(lambda ss: ss[0], exception_triples))

        self.exception_degree_base2ss = defaultdict(list)
        degrees = [ComparativeDegree.BASE, ComparativeDegree.COMP,
                   ComparativeDegree.SUPER]
        for triple in exception_triples:
            for degree, word in zip(degrees, triple):
                self.exception_degree_base2ss[(degree, triple[0])].append(word)

        self.base_is_er_est = set(base_is_er_est)
        self.erable = set(erable)
        self.not_erable = set(not_erable)

        self.degree_polarity2adverb = {
            (ComparativeDegree.BASE,  ComparativePolarity.POS): None,
            (ComparativeDegree.COMP,  ComparativePolarity.POS): 'more',
            (ComparativeDegree.SUPER, ComparativePolarity.POS): 'most',
            (ComparativeDegree.BASE,  ComparativePolarity.NEG): 'not',
            (ComparativeDegree.COMP,  ComparativePolarity.NEG): 'less',
            (ComparativeDegree.SUPER, ComparativePolarity.NEG): 'least',
        }
        self.adverb2degree_polarity = v2k_from_k2v(self.degree_polarity2adverb)

        self.repeat_last_chr_re = re.compile('.*[^aeiou][aeiou][^aeiouyw]$')

    @staticmethod
    def from_file(syllable_counter, fn):
        j = yaml.load(open(fn))
        exceptions = []
        for line in j['exceptions']:
            base, er, est = line.split()
            exceptions.append((base, er, est))
        base_is_er_est = j['base_is_er_est']
        erable = j['erable']
        not_erable = j['not_erable']
        return ComparativeManager(
            syllable_counter, exceptions, base_is_er_est, erable, not_erable)

    @staticmethod
    def default(syllable_counter):
        fn = 'panoptes/ling/morph/comparative/comparative.yaml'
        return ComparativeManager.from_file(syllable_counter, fn)

    def is_erable(self, base):
        if base in self.exception_bases:
            return True

        if base in self.erable:
            return True

        if base in self.not_erable:
            return False

        n = self.syllable_counter.get_syllable_count(base)
        if n == 1:
            if base.endswith('ed'):
                r = False
            else:
                r = True
        elif n == 2:
            if base[-1] in 'wy':
                r = True
            elif 2 <= len(base) and base[-2:] in ['le']:
                r = True
            elif 3 <= len(base) and base[-3:] in ['ear', 'eer', 'ver']:
                r = True
            else:
                r = False
        else:
            r = False
        return r

    def repeat_last_chr(self, base):
        n = self.syllable_counter.get_syllable_count(base)
        if 1 < n:
            return False

        return self.repeat_last_chr_re.match(base)

    def ending_i_or_y(self, base):
        assert base[-1] == 'y'

        if len(base) == 1:
            return 'y'

        if base[-2] in 'aeiouy':
            return 'y'
        else:
            return 'i'

    def encode_er_est(self, degree, base):
        """
        (degree, base form) -> derived form
        """
        # The base form is the canonical form.
        if degree == ComparativeDegree.BASE:
            return base

        # Check exceptions.
        ss = self.exception_degree_base2ss.get((degree, base))
        if ss:
            return ss[0]

        if degree == ComparativeDegree.COMP:
            if base[-1] == 'y':
                return base[:-1] + self.ending_i_or_y(base) + 'er'
            elif base[-1] == 'e':
                return base + 'r'
            else:
                if self.repeat_last_chr(base):
                    return base + base[-1] + 'er'
                else:
                    return base + 'er'
        elif degree == ComparativeDegree.SUPER:
            if base[-1] == 'y':
                return base[:-1] + self.ending_i_or_y(base) + 'est'
            elif base[-1] == 'e':
                return base + 'st'
            else:
                if self.repeat_last_chr(base):
                    return base + base[-1] + 'est'
                else:
                    return base + 'est'
        else:
            assert False

    def encode(self, degree, polarity, base):
        """
        (degree, polarity, base) -> (None, adjier) or (more, adjy)
        """
        assert base
        if polarity == ComparativePolarity.POS and self.is_erable(base):
            adverb = None
            word = self.encode_er_est(degree, base)
        else:
            adverb = self.degree_polarity2adverb[(degree, polarity)]
            word = base
        return adverb, word

    def decode_er_est(self, word):
        # Exceptions (they cover every possibility for the words they include).
        degrees_bases = self.exception_s2degrees_bases.get(word)
        if degrees_bases:
            return degrees_bases

        # Catch positive (base) forms with derived-looking endings (eg, modest,
        # clever, etc).
        if word in self.base_er_est:
            return [(ComparativeDegree.BASE, word)]

        # -er and -est derivations work and reverse the same way.
        degrees_bases = []
        for suffix, degree in [('er', ComparativeDegree.COMP),
                               ('est', ComparativeDegree.SUPER)]:
            if word.endswith(suffix):
                base = word[:-len(suffix)]
                if 2 <= len(base) and base[-2] == base[-1] and \
                        self.repeat_last_chr(base[:-1]):
                    degrees_bases.append((degree, base[:-1]))
                else:
                    degrees_bases.append((degree, base))
                    degrees_bases.append((degree, base + 'e'))

        # Not -er or -est, so it's the base form.
        if not degrees_bases:
            return [(ComparativeDegree.BASE, word)]

        # -i back to -y.
        #
        # It is almost always y (exceptions seem to be all nationalities, eg
        # Iraqi).
        rr = []
        for degree, base in degrees_bases:
            if base[-1] != 'i':
                pass
            elif base[0].isupper():
                pass
            else:
                base = base[:-1] + 'y'
            rr.append((degree, base))
        return rr

    def decode(self, adverb, word):
        """
        (None, adjier) or (more, adjy) -> list of (degree, polarity, base)
        """
        r = self.adverb2degree_polarity.get(adverb)
        if not r:
            return []
        adverb_degree, polarity = r

        # No adverb, so degree is found in the derived form.
        if adverb_degree == ComparativeDegree.BASE and \
                polarity == ComparativePolarity.POS:
            degrees_bases = self.decode_er_est(word)
            return zip(lambda (deg, base): (deg, polarity, base), degrees_bases)

        # Has an adverb, so the word is in its base form.
        return [(adverb_degree, polarity, word)]
