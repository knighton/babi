import codecs
from glob import glob


def get_problems(d):
    ff = glob(d + 'qa6*train*')
    print d, ff
    f = ff[0]
    ss = codecs.open(f, encoding='utf-8').readlines()
    lines = map(lambda s: s.strip(), ss)

    problems = []
    cur_prob = []
    prev_n = 0
    for line in lines:
        ss = line.split()
        n = int(ss[0])
        line = line[len(ss[0]) + 1:]
        if n < prev_n:
            problems.append(cur_prob)
            cur_prob = []

        ss = line.split('\t')
        if len(ss) == 1:
            in_s, out_s = ss[0], None
        elif len(ss) == 3:
            in_s, out_s = ss[0], ss[1]
        else:
            assert False
        cur_prob.append((in_s, out_s))
        prev_n = n

    for g in problems[:2]:
        for pair in g:
            print pair
        print

    return problems
