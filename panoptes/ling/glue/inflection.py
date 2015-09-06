# "inflection" here means the single concept connecting choices of verb
# conjugation, personal pronoun, etc.

from base.enum import enum
from ling.glue.grammatical_number import N2


Declension = enum("""Declension =
    I WE YOU YALL HE SHE IT THEY1 ONE WHO1 WHO2 THEY2 WHOEVER1 WHOEVER2""")


def is_declension_q(d):
    return d in (Declension.WHO1, Declension.WHO2, Declension.WHOEVER1,
                 Declension.WHOEVER2)


Person = enum('Person = FIRST SECOND THIRD')


Conjugation = enum('Conjugation = S1 S2 S3 P1 P2 P3')


CONJ2INDEX = dict(zip(sorted(Conjugation.values),
                      range(len(Conjugation.values))))


N2_TO_CONJ = {
    N2.SING: Conjugation.S3,
    N2.PLUR: Conjugation.P3,
}


Gender = enum('Gender = MALE FEMALE NEUTER')


class PerNumGen(object):
    def __init__(self, person, number, gender):
        self.person = person
        self.number = number
        self.gender = gender
        assert Person.is_valid(self.person)
        assert N2.is_valid(self.number)
        assert Gender.is_valid(self.gender)


class InflectionInfo(object):
    def __init__(self, declension, usual_conjugation, number, gender,
                 person_groups):
        # Personal pronoun, augmented with number for uniform conjugation.
        #
        # Conflates person, number, gender, and a little bit more (eg, WHO vs
        # WHOEVER, THEY1 vs ONE vs HE, etc).
        self.declension = declension
        assert Declension.is_valid(self.declension)

        # Form used when conjugating verbs (3 persons x 2 numbers).
        self.usual_conjugation = usual_conjugation
        assert Conjugation.is_valid(self.usual_conjugation)

        # Number: singulr or plural.
        #
        # This is about the count of the underlying thing(s) in question, not
        # grammatical number.
        self.number = number
        assert N2.is_valid(self.number)

        # Gender: male, female, neuter, any (None).
        self.gender = gender
        if self.gender:
            assert Gender.is_valid(self.gender)

        # List of possible groupings of person it could refer to.
        #
        # Only WE and YOU2 have multiple options.
        self.person_groups = person_groups
        for pg in self.person_groups:
            for p in pg:
                assert Person.is_valid(p)

    def decide_conjugation(self, is_bare_pers_pro):
        # It's a little more complicated because we allow singular they:
        #
        #   "someone (THEY1, not pers pro) is here"
        #   "they (THEY1, is pers pro) are here"
        if is_bare_pers_pro:
            if self.declension == Declension.THEY1:
                return Conjugation.P3  # Conjugate as third person plural.

        return self.usual_conjugation


class InflectionManager(object):
    """
    Decides which inflection to use (in normal situations).
    """

    def __init__(self):
        # For number = 1, person = 3 only.
        self.special_gender2declension = {
            Gender.MALE:   Declension.HE,
            Gender.FEMALE: Declension.SHE,
            Gender.NEUTER: Declension.IT,
            None:          Declension.THEY1,
        }

        # All other cases.
        self.special_number2declension = {
            (N2.SING, Person.FIRST):  Declension.I,
            (N2.SING, Person.SECOND): Declension.YOU,
            (N2.PLUR, Person.FIRST):  Declension.WE,
            (N2.PLUR, Person.SECOND): Declension.YALL,
            (N2.PLUR, Person.THIRD):  Declension.THEY2,
        }

        # Easy name -> list of groups of first/second/third person.
        s2pgroups = {
            '1': [
                [Person.FIRST]
            ],
            '2': [
                [Person.SECOND]
            ],
            '3': [
                [Person.THIRD]
            ],
            '1+': [
                [Person.FIRST],
                [Person.FIRST, Person.SECOND],
                [Person.FIRST, Person.THIRD],
                [Person.FIRST, Person.SECOND, Person.THIRD]
            ],
            '2+': [
                [Person.SECOND],
                [Person.SECOND, Person.THIRD]
            ],
            '?': [],  # Users of this (eg, "who") are handled differently.
        }

        # Data to associate declensions, conjugations, genders, and persons.
        #
        # Note: question terms ('who' and 'whoever' forms) are swapped out for
        # their common noun equivalents during encode/decode (who -> what
        # person, etc).  They are outside 'person groups' characterizations.
        data = """
            I         S1  ANY     1
            WE        P1  ANY     1+
            YOU1      S2  ANY     2
            YOU2      P2  ANY     2+
            HE        S3  MALE    3
            SHE       S3  FEMALE  3
            IT        S3  NEUTER  3
            THEY1     S3  ANY     3
            ONE       S3  ANY     3
            WHO1      S3  ANY     ?
            WHO2      S3  ANY     ?
            THEY2     P3  ANY     3
            WHOEVER1  P3  ANY     ?
            WHOEVER2  P3  ANY     ?
        """

        self.declension2info = {}
        for line in data.strip().split('\n'):
            dec, conj, gender, pgroups = line.split()
            dec = Declension.from_str[dec]
            usual_conj = Conjugation.from_str[conj]
            number = N2.SING if 'S' in gender else N2.PLUR
            gender = Gender.from_str[gender]
            person_groups = s2pgroups[pgroups]
            info = InflectionInfo(
                dec, usual_conj, number, gender, person_groups)
            self.declension2info[dec] = info

    def decide_declension(self, pp):
        """
        list of PerNumGen -> correct declension for those people
        """
        assert pp
        if len(pp) == 1:
            p = pp[0]
            if p.number == N2.SING and p.person == Person.THIRD:
                r = self.special_gender2declension[p.gender]
            else:
                r = self.special_number2declension[(p.number, p.person)]
        else:
            persons = map(lambda p: p.person, pp)
            if Person.FIRST in persons:
                r = Declension.WE
            elif Person.SECOND in persons:
                r = Declension.YALL
            else:
                r = Declension.THEY2
        return r

    def get_declension(self, declension):
        return self.declension2info[declension]
