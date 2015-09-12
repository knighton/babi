from panoptes.etc.dicts import v2kk_from_k2v, v2k_from_k2v
from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Conjugation, Declension
from panoptes.ling.glue.magic_token import POSSESSIVE_MARK
from panoptes.ling.tree.base import ArgPosRestriction
from panoptes.ling.tree.common.base import CommonArgument


PersonalPronounCase = enum('PersonalPronounCase = SUBJECT OBJECT REFLEXIVE')


# PersonalPronounCase -> ArgPosRestriction.
PPCASE2ARG_POS_RES = {
    PersonalPronounCase.SUBJECT: ArgPosRestriction.SUBJECT,
    PersonalPronounCase.OBJECT: ArgPosRestriction.NOT_SUBJECT,
    PersonalPronounCase.REFLEXIVE: ArgPosRestriction.NOT_SUBJECT,
}


class PersonalPronoun(CommonArgument):
    """
    (Non-possessive) personal pronouns.
    """

    def __init__(self, declension, ppcase):
        self.declension = declension
        assert Declension.is_valid(self.declension)

        self.ppcase = ppcase
        assert PersonalPronounCase.is_valid(self.ppcase)

    def arg_position_restriction(self):
        # This is not called for personal determiners, which exclusively are
        # found in the cor_or_pos field of common nouns, so we're fine.
        return PPCASE2ARG_POS_RES[self.ppcase]

    def decide_conjugation(self, state, idiolect, context):
        return state.personal_mgr.perspro_decide_conjugation(self)

    def say(self, state, idiolect, context):
        return state.personal_mgr.perspro_say(self, idiolect.whom)


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
            s = sss[row_index + 1][col_index + 1]
            if s == invalid_entry:
                continue

            row = sss[row_index + 1][0]
            row = row_enum.from_str[row]

            col = sss[0][col_index]
            col = col_enum.from_str[col]

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
        I        i       me       myself     mine      my
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
    """

    r = table_from_str(
        text, row_enum=Declension, col_enum=PersonalColumn, invalid_entry='X')

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
    """
    Personal pronouns are represented as the PersonalPronoun verb arg.

    The other two types, possessive determiners and possessive pronouns, are
    stored in the 'cor_dec_pos' field in CommonNoun in surface structure.
    """

    def __init__(self, inflection_mgr):
        self.inflection_mgr = inflection_mgr

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
        info = self.inflection_mgr.get_declension(p.declension)
        return info.decide_conjugation(True)

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
