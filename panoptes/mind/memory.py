


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
        pass

    def decode_personal_pronoun(self, deep_ref, from_xx, to_xx):
        arg = deep_ref.arg

        if arg.is_interrogative():
            who = make_who()
            x = self.add_item(who)
            return [x]

        previously_in_clause = arg.ppcase = PersonalPronounCase.REFLEXIVE

        info = self.inflection_mgr.get(args.declension)
        xxx = []
        for group in info.person_groups:
            xx = []

            if 1 in group:
                xx += from_xx

            if 2 in group:
                xx += to_xx

            if 3 in group:
                assert False  # TODO

            xxx.append(xx)
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
