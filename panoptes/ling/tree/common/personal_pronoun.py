from base.dicts import v2kk_from_k2v, v2k_from_k2v
from base.enum import enum
from ling.glue.inflection import Conjugation, Declension
from ling.glue.magic_token import POSSESSIVE_MARK
from ling.tree.common.base import *


PersonalPronounCase = enum('PersonalPronounCase = SUBJECT OBJECT REFLEXIVE')


# PersonalPronounCase -> ArgPosRestriction.
PPCASE2ARG_POS_RES = {
    PersonalPronounCase.SUBJECT: ArgPosRestriction.SUBJECT,
    PersonalPronounCase.OBJECT: ArgPosRestriction.NOT_SUBJECT,
    PersonalPronounCase.REFLEXIVE: ArgPositionRestriction.NOT_SUBJECT,
}


class PersonalPronoun(Argument):
    def __init__(self, ppcase, declension):
        # This field is none for personal determiners.
        self.ppcase = ppcase
        if self.ppcase is not None:
            assert PersonalPronounCase.is_valid(self.ppcase)

        self.declension = declension
        assert Declension.is_valid(self.declension)

    def arg_position_restriction(self):
        # This is not called for personal determiners, which exclusively are
        # found in the cor_or_pos field of common nouns, so we're fine.
        return PPCASE2ARG_POS_RES[self.ppcase]

    def decide_conjugation(self):
        # Call manager class.
        assert False

    def say(self, context):
        # Call manager class.
        assert False


def table_from_str(s, row_enum, col_enum, invalid_entry):
    """
    Some text -> mapping of (row, col) -> entry
    """
    ss = s.strip().split('\n')
    sss = map(lambda s: s.split(), ss)

    n = len(sss[0])
    for ss in sss[1:]:
        assert len(ss) == n + 1

    r = {}
    for row_index in xrange(len(sss) - 1):
        for col_index in xrange(n):
            row = sss[row_index + 1][0]
            row = row_enum.from_str[row]
            col = sss[0][col_index + 1]
            col = col_enum.from_str[col]
            s = sss[row_index + 1][col_index + 1]
            if s == invalid_entry:
                continue
            if s.endswith("'s"):
                entry = (s[:-2], POSSESSIVE_MARK)
            else:
                entry = s,
            r[(row, col)] = entry
    return r


PersonalColumn = enum('PersonalColumn = SUBJ OBJ REFL POS_PRO POS_DET')


def make_table(use_whom):
    text = """
                 SUBJ    OBJ      REFL       POS_PRO   POS_DET
        I        I       me       myself     mine      my
        YOU      you     you      yourself   yours     your
        HE       he      him      himself    his       his
        SHE      she     her      herself    hers      her
        IT       it      it       itself     its       its
        THEY1    they    them     themself   theirs    their
        ONE      one     one      oneself    one's     one's
        WE       we      us       ourselves  ours      our
        YALL     you     you      yourselves yours     your
        THEY2    they    them     themselves theirs    their
        WHO1     who     whom     X          whose     whose
        WHO2     who     whom     X          whose     whose
        WHOEVER1 whoever whomever X          whoever's whoever's
        WHOEVER2 whoever whomever X          whoever's whoever's
    """)

    r = table_from_str(
        text, row_enum=PersonalColumn, col_enum=Declension, invalid_entry='X')

    if not use_whom:
        r[(Declension.WHO1, PersonalColumn.OBJ)] = 'who',
        r[(Declension.WHO2, PersonalColumn.OBJ)] = 'who',
        r[(Declension.WHOEVER1, PersonalColumn.OBJ)] = 'whoever',
        r[(Declension.WHOEVER2, PersonalColumn.OBJ)] = 'whoever',

    return r


class PersonalTable(object):
    def __init__(self, dec_pc2ss):
        # (Declension, PersonalColumn) -> tokens.
        self.dec_pc2ss = dec_pc2ss

        # Tokens -> list of (Declension, PersonalColumn).
        self.ss2decs_pcs = v2kk_from_k2v(dec_pc2ss)

    def say(self, dec, pc):
        """
        Declension, PersonalColumn -> tokens
        """
        return self.dec_pc2ss[(dec, pc)]

    def parse(self, ss):
        """
        tokens -> list of (Declension, PersonalColumn)
        """
        return self.ss2decs_pcs[tuple(ss)]


class PersonalKnowledge(object):
    def __init__(self):
        self.who = PersonalTable(make_table(False))
        self.whom = PersonalTable(make_table(True))

    def say(self, dec, pc, use_whom):
        if use_whom:
            return self.whom.say(dec, pc)
        else:
            return self.who.say(dec_pc)

    def parse(self, ss):
        return sorted(set(self.who.parse(ss) + self.whom.parse(ss)))


class PersonalManager(object):
    def __init__(self, inflect_mgr):
        self.inflect_mgr = inflect_mgr

        self.ppcase2pc = {
            PersonalPronounCase.SUBJECT: PersonalColumn.SUBJ,
            PersonalPronounCase.OBJECT: PersonalColumn.OBJ,
            PersonalPronounCase.REFLEXIVE: PersonalColumn.REFL,
        }

        self.pc2ppcase = v2k_from_k2v(self.ppcase2pc)

        self.tables = PersonalKnowledge()

    def perspro_parse(self, ss):
        """
        tokens -> possible PersonalPronouns
        """
        pp = []
        for dec, pc in self.tables.parse(ss):
            ppc = self.pc2ppcase.get(pc)
            if not ppc:
                continue
            p = PersonalPronoun(dec, ppc)
            pp.append(p)
        return pp

    def perspro_decide_conjugation(self, p):
        """
        PersonalPronoun -> Conjugation
        """
        dec = self.inflect_mgr.get_declension(p.declension)
        return dec.decide_conjugation(True)

    def perspro_say(self, p, use_whom):
        """
        PersonalPronoun, who/whom -> tokens
        """
        pc = self.ppcase2pc[p.ppcase]
        ss = self.tables.say(p.declension, pc, use_whom)
        conj = self.personal_pronoun_decide_conjugation(p)
        return SayResult(tokens=ss, conjugation=conj, eat_prep=False)

    def pospro_parse(self, ss):
        """
        tokens -> possible Declensions if possessive pronoun
        """
        decs = []
        for dec, pc in self.tables.parse(ss):
            if pc != PersonalColumn.POS_PRO:
                continue
            decs.append(dec)
        return decs

    def pospro_say(self, dec, use_whom):
        """
        Declension, who/whom -> tokens
        """
        return self.tables.say(dec, PersonalColumn.POS_PRO, use_whom)

    def posdet_parse(self, ss):
        """
        tokens -> possible Declensions if possessive determiner
        """
        decs = []
        for dec, pc in self.tables.parse(ss):
            if pc != PersonalColumn.POS_DET:
                continue
            decs.append(dec)
        return decs

    def posdet_say(self, dec, use_whom):
        """
        Declension, who/whom -> tokens
        """
        return self.tables.say(dec, PersonalColumn.POS_DET, use_whom)
