from collections import defaultdict


def collapse_int_tuples_to_wildcards(tuples, num_options_per_field):
    """
    int tuples, num options per field -> tuples with wildcards
    """
    while True:
        best_new_tuples = tuples
        give_up = True

        for field_index, num_options in enumerate(num_options_per_field):
            already_collapsed = []
            wildcarded2options_present = defaultdict(set)
            for nn in tuples:
                option = nn[field_index]
                if option == num_options:
                    already_collapsed.append(nn)
                    continue
                wildcarded = list(nn)
                wildcarded[field_index] = num_options
                wildcarded = tuple(wildcarded)
                wildcarded2options_present[wildcarded].add(option)

            collapsed_or_not = []
            for wildcarded, options_present in \
                    wildcarded2options_present.iteritems():
                nn = list(wildcarded)
                if len(options_present) == num_options:
                    nn[field_index] = num_options
                    collapsed_or_not.append(nn)
                else:
                    for option in options_present:
                        nn[field_index] = option
                        collapsed_or_not.append(list(nn))

            new_tuples = already_collapsed + collapsed_or_not
            if len(new_tuples) < len(best_new_tuples):
                best_new_tuples = new_tuples
                give_up = False

        if give_up:
            break

        tuples = best_new_tuples
    return tuples


def expand_helper(nn, num_options_per_field, index):
    if index == len(num_options_per_field):
        yield []
        return

    num_options = num_options_per_field[index]
    if nn[index] < num_options:
        for tail in expand_helper(nn, num_options_per_field, index + 1):
            yield [nn[index]] + tail
    else:
        for n in xrange(num_options):
            for tail in expand_helper(nn, num_options_per_field, index + 1):
                yield [n] + tail


def expand_int_tuples_from_wildcards(tuples, num_options_per_field):
    """
    int tuples, num options per field -> tuples without wildcards
    """
    rr = []
    for nn in tuples:
        for r in expand_helper(nn, num_options_per_field, 0):
            rr.append(r)
    return rr
