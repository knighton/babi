def each_choose_one_from_each(sss):
    """
    List of lists -> yields every combination of one item from each list
    """
    if not all(sss):
        return

    sss2 = []
    for ss in sss:
        sss2.append(tuple(ss))

    zz = map(lambda ss: len(ss) - 1, sss2)
    ii = [0] * len(sss2)
    while True:
        yield map(lambda (ss, i): ss[i], zip(sss2, ii))
        ok = False
        for pos in range(len(ii)):
            if ii[pos] == zz[pos]:
                ii[pos] = 0
            else:
                ii[pos] += 1
                ok = True
                break
        if not ok:
            break


def int_from_tuple(aa, options_per_field):
    """
    tuple, options per field -> integer

    Corresponds to tuple_from_int().
    """
    n = 0
    mul = 1
    for a, options in zip(aa, options_per_field):
        n += options.index(a) * mul
        mul *= len(options)
    return n


def tuple_from_int(n, options_per_field):
    """
    integer, options per field -> tuple

    Corresponds to int_from_tuple().
    """
    aa = []
    for options in options_per_field:
        a = options[n % len(options)]
        aa.append(a)
        n /= len(options)
    return aa
