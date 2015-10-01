

















"""
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
"""
