def final_repeat_len(s):
    assert s
    match = s[-1]
    for i in xrange(len(s) - 2, -1, -1):
        if s[i] != match:
            return len(s) - i - 1
    return len(s)


class SuffixTransform(object):
    """
    A reversible transformation that turns one string into another.
    """

    def __init__(self, truncate, repeat, append):
        self.truncate = truncate
        assert isinstance(self.truncate, str)

        self.repeat = repeat
        assert isinstance(self.repeat, int)

        self.append = append
        assert isinstance(self.append, str)

    @staticmethod
    def from_before_after(before, after):
        for i in range(len(before), 0, -1):
            base = before[:i]
            truncate = before[i:]
            for repeat in range(final_repeat_len(base), -1, -1):
                base_repeat = base + base[-1] * repeat
                if after.startswith(base_repeat):
                    append = after[len(base_repeat):]
                    return SuffixTransform(truncate, repeat, append)
        return SuffixTransform(before, 0, after)

    def to_d(self):
        return {
            'truncate': self.truncate,
            'repeat': self.repeat,
            'append': self.append,
        }

    def transform(self, orig):
        """
        orig -> transformed

        Apply the transformation.
        """
        assert orig.endswith(self.truncate)
        s = orig[:len(orig) - len(self.truncate)]
        if self.repeat:
            s += s[-1] * self.repeat
        return s + self.append

    def inverse_transform(self, transformed):
        """
        transformed -> orig

        Reverse the transformation.
        """
        s = transformed
        if not s.endswith(self.append):
            return None
        s = s[:len(s) - len(self.append)]
        if self.repeat:
            if not s or not s.endswith(s[-1] * self.repeat):
                return None
            s = s[:-self.repeat]
        return s + self.truncate
