def make_special_mapping(first_n, ss):
    n2s = {}
    s2n = {}
    for i, s in enumerate(ss):
        assert s not in s2n
        n = first_n + i
        n2s[n] = s
        s2n[s] = n
    return n2s, s2n
