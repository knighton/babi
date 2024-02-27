import re


class AOrAnClassifier(object):
    """
    Decide between "a" and "an".
    """

    def __init__(self):
        # A/an-picking from the Linguistics ruby gem by Michael Granger:
        # http://www.deveiate.org/projects/Linguistics/wiki/English
        rules = [
            # Exceptions (an honor).
            ('euler|hour(?!i)|heir|honest|hono', 'an'),

            # Abbreviations:
            # Strings of capitals starting with a vowel-sound consonant followed
            # by another consonant, and which are not likely to be real words.
            (('(?!FJO|[HLMNS]Y.|RY[EO]|SQU|(F[LR]?|[HL]|MN?|N|RH?|'
              'S[CHKLMNPTVW]?|X(YL)?)[AEIOU])[FHLMNRSX][A-Z]'), 'an'),

            ('^[aefhilmnorsx][.-]', 'an'),
            ('^[a-z][.-]', 'a'),

            ('^[^aeiouy]', 'a'),
            ('^e[uw]', 'a'),                 # eu like "you" (a European).
            ('^onc?e', 'a'),                 # o like "wa" (a one-liner).
            ('uni([^nmd]|mo)', 'a'),         # u like "you" (a university).
            ('^u[bcfhjkqrst][aeiou]', 'a'),  # u like "you" (a uterus).
            ('^[aeiou]', 'an'),              # Vowels (an owl).
                                             # y like i (an yclept).
            ('y(b[lor]|cl[ea]|fere|gg|p[ios]|rou|tt)', 'an'),
            ('', 'a')                        # Guess "a".
        ]

        self.rules = [(re.compile(r_a[0]), r_a[1]) for r_a in rules]

    def classify(self, next_word):
        for r, a in self.rules:
            if r.search(next_word):
                return a
