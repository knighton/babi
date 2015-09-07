from collections import defaultdict


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


def collapse_int_tuples_to_wildcards(tuples, num_options_per_field):
    """
    int tuples, num options per field -> tuples with "wildcards"
    """
    # Keep greedily shrinking tuples until we can't anymore.
    while True:
        best_new_tuples = tuples
        give_up = True

        # For each field to collapse on,
        for field_index, num_options in enumerate(num_options_per_field):
            # For each tuple,
            wildcarded2options_present = defaultdict(set)
            for aa in tuples:
                option = aa[field_index]

                # If we've already collapsed on this field, skip it.
                if option == num_options:
                    continue

                # Create the tuple's lookup key with wildcard.
                wildcarded = list(aa)
                wildcarded[field_index] = num_options
                wildcarded = tuple(wildcarded)

                # Set the present bit for this option.
                wildcarded2options_present[wildcarded].add(option)

            # For each key,
            tmp_new_tuples = []
            for wildcarded, options_present in \
                    wildcarded2options_present.iteritems():
                # Unpack the tuple's wildcarded lookup key.
                aa = list(wildcarded)

                # If all options are present, collapse it, else, don't.
                if len(options_present) == num_options:
                    aa[field_index] = num_options
                    tmp_new_tuples.append(aa)
                else:
                    for option in options_present:
                        aa[field_index] = option
                        tmp_new_tuples.append(aa)

            # If we did a better job than the existing, keep it.
            if tmp_new_tuples and len(tmp_new_tuples) < len(best_new_tuples):
                best_new_tuples = tmp_new_tuples
                give_up = False

        # If none of the fields were able to collapse anything, give up.
        if give_up:
            break

        tuples = best_new_tuples

    return tuples
