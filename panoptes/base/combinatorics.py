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

