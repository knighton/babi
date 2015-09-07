from collections import defaultdict


def v2kk_from_k2v(k2v):
    v2kk = defaultdict(list)
    for k, v in k2v.iteritems():
        v2kk[v].append(k)
    return v2kk


def v2k_from_k2v(k2v):
    v2k = {}
    for k, v in k2v.iteritems():
        v2k[v] = k
    return v2k


def v2k_from_k2vv(k2vv):
    v2k = {}
    for k, vv in k2vv.iteritems():
        for v in vv:
            v2k[v] = k
    return v2k
