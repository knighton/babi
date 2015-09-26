import codecs
from glob import glob

from panoptes.dataset.dataset import Dataset, Task, Episode


def int_from_fn(f):
    x = f.rindex('/')
    f = f[x + 1:]
    assert f.startswith('qa')
    f = f[2:]
    x = f.index('_')
    s = f[:x]
    return int(s)


def name_from_fn(f):
    x = f.rindex('/')
    f = f[x + 1:]
    assert f.startswith('qa')
    f = f[2:]
    x = f.index('_')
    f = f[x + 1:]

    s = '_train.txt'
    if f.endswith(s):
        return f[:-len(s)]
    
    s = '_test.txt'
    if f.endswith(s):
        return f[:-len(s)]

    assert False


def task_from_fn(fn):
    name = name_from_fn(fn)
    episodes = []
    pairs = []
    prev_n = None
    with codecs.open(fn, encoding='utf-8') as f:
        for line in f:
            x = line.find(' ')
            n = int(line[:x])
            line = line[x + 1:]
            if n < prev_n:
                episodes.append(Episode(pairs))
                pairs = []
            ss = line.strip().split('\t')
            if len(ss) == 1:
                in_s, out_s = ss[0], None
            elif len(ss) == 3:
                in_s, out_s = ss[0], ss[1]
            else:
                assert False
            pairs.append((in_s, out_s))
            prev_n = n
    return Task(name, episodes)


def load_babi(d):
    ff = glob(d + '/*test.txt')
    nn_ff = map(lambda f: (int_from_fn(f), f), ff)
    nn_ff.sort()
    tasks = []
    for n, f in nn_ff:
        task = task_from_fn(f)
        tasks.append(task)
    return Dataset('babi', tasks)
