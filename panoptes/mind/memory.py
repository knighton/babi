


class DeepReference(object):
    """
    Used in resolving DeepArguments.
    """

    def __init__(self, owning_clause_id, is_subj, arg):
        # We need to know if referents are from the same clause in order to
        # handle reflexives.
        self.owning_clause_id = owning_clause_id

        # Whether subject or not.  Needed for personal pronouns (I vs me).
        self.is_subj = is_subj

        # The actual argument. 
        self.arg = arg


class MemoryReference(object):
    """
    Used in expressing MemoryItems.
    """

    def __init__(self, owning_clause_id, is_subj, xx):
        # Reflexives are intra-clause (eg, "You know you know yourself").
        self.owning_clause_id = owning_clause_id

        # Affects case (eg, "I" vs "me").
        self.is_subj = is_subj

        # Nonempty list of sorted, unique memory item indexes (eg, "no one" is a
        # common noun where the correlative is NEG).
        self.xx = xx


class Memory(object):
    def __init__(self):
        self.items = []

    def are_singular(self, xx):
        if len(xx) != 1:
            return False

        x, = xx
        return self.items[x].is_singular()

    def get_activated(self, is_singular, is_animate, gender):
        assert False  # XXX

    def decode_personal_pronoun(self, deep_ref, from_xx, to_xx):
        arg = deep_ref.arg

        if arg.is_interrogative():
            who = make_who()
            x = self.add_item(who)
            return [x]

        previously_in_clause = arg.ppcase = PersonalPronounCase.REFLEXIVE

        d = args.declension

        if d == Declension.I:
            if not self.are_singular(from_xx):
                return []
            xxx = [from_xx]
        elif d == Declension.WE:
            xxx = []
            for me in [[], from_xx]:
                for you in [[], to_xx]:
                    for other in self.get_activated(None, None, None):
                        xx = me + you + other
                        if self.are_singular(xx):
                            continue
                        xxx.append(xx)
        elif d == Declension.YOU:
            if not self.are_singular(to_xx):
                return []
            xxx = [to_xx]
        elif d == Declension.YALL:
            if self.are_singular(to_xx):
                return []
            xxx = [to_xx]
            for other in self.get_activated(None, None, None):
                xxx.append(to_xx + other)
        elif d == Declension.HE:
            xxx = self.get_activated(True, True, Gender.MALE)
        elif d == Declension.SHE:
            xxx = self.get_activated(True, True, Gender.FEMALE)
        elif d == Declension.IT:
            xxx = self.get_activated(True, False, Gender.NEUTER)
        elif d == Declension.THEY1:
            xxx = self.get_activated(True, True, None)
        elif d == Declension.ONE:
            xxx = self.get_activated(True, True, None)
        elif d == Declension.THEY2:
            xxx = self.get_activated(False, None, None)
        else:
            assert False

        return xxx

    def decode_proper_noun(self, deep_ref, from_xx, to_xx):
        arg = deep_ref.arg

        xx = self.name2xx[arg.name]

        if not xx:
            item = person_from_name(arg.name)
            x = self.add_item(item)
            xx = [x]

        return xx

    def decode(self, dsen, from_xx, to_xx):
        XXX
