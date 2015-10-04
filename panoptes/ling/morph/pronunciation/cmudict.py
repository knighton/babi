from collections import defaultdict


def each_line(fn):
    with open(fn) as f:
        for line in f:
            x = line.find(';;;')
            if x != -1:
                line = line[:x]
            line = line.strip()
            if not line:
                continue
            yield line


def parse_word(s):
    if not s:
        return None

    s = s.lower()

    # For example, "AXES(1)" is the second pronunciation entry for "AXES".
    if s.endswith(')'):
        if len(s) < 4:
            return None

        if s[-3] != '(':
            return None

        try:
            int(s[-2])
        except:
            return None

        s = s[:-3]

    if not s[0].isalpha():
        return None

    return s


class CmuDict(object):
    def __init__(self, word2pronuns):
        self.word2pronuns = word2pronuns

    @staticmethod
    def from_file(fn):
        word2pronuns = defaultdict(list)
        for line in each_line(fn):
            ss = line.split()
            if len(ss) < 2:
                continue

            word = parse_word(ss[0])
            if not word:
                continue

            word2pronuns[word].append(ss[1:])
        return CmuDict(word2pronuns)

    @staticmethod
    def default():
        fn = 'panoptes/ling/morph/pronunciation/cmudict-0.7b.txt'
        return CmuDict.from_file(fn)

    def get_syllable_counts(self, word):
        nn = set()
        for ss in self.word2pronuns[word]:
            n = sum(map(lambda s: s[-1].isdigit(), ss))
            nn.add(n)
        return sorted(nn)
