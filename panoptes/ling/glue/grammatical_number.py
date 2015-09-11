# Support for grammatical number.
#
# Grammatical number shows up in different ways in English with varying levels
# of ambiguity, such as singular/plural, which/what, verb conjugation, etc.

from collections import defaultdict

from panoptes.etc.enum import enum


N2 = enum('N2 = SING PLUR')


N3 = enum('N3 = ZERO SING PLUR')


N5 = enum('N5 = ZERO SING DUAL FEW MANY')


def join_disjoint_sets(ss):
    r = set()
    for s in ss:
        for a in s:
            r.add(a)
    return r

def join_disjoint_dicts(k2vs):
    r = {}
    for k2v in k2vs:
        for k, v in k2v.iteritems():
            r[k] = v
    return r


class NX(object):
    pass


NXS = [N5, N3, N2]
NX.values = join_disjoint_sets(map(lambda nx: nx.values, NXS))
NX.to_str = join_disjoint_dicts(map(lambda nx: nx.to_str, NXS))


def reduce_spans(aa):
    """
    Drop subsumed spans and combine adjacent and overlapping ones.
    """
    if not aa:
        return aa

    # Sort the spans.
    aa = sorted(aa)

    # If any extend infinitely to the right, drop everything after that.
    for x, a in enumerate(aa):
        if a[1] == -1:  # -1 means no limit.
            aa = aa[:x + 1]

    # Now, walk the list and join adjacent or overlapping spans.
    aa2 = []
    prev_a = None
    for a in aa:
        if prev_a:
            if not (prev_a[1] < a[0]):
                prev_a = (prev_a[0], max(prev_a[1], a[1]))
            else:
                aa2.append(prev_a)
                prev_a = None
        else:
            prev_a = a
    if prev_a:
        aa2.append(prev_a)

    return aa2


class GrammaticalNumberManager(object):
    def __init__(self):
        # Each NX's words for the same group of spans (defined below).
        self.class2col2nx = {
            #    0        1        2        3..30    30..
            N5: [N5.ZERO, N5.SING, N5.DUAL, N5.FEW,  N5.MANY],
            N3: [N3.ZERO, N3.SING, N3.PLUR, N3.PLUR, N3.PLUR],
            N2: [N2.PLUR, N2.SING, N2.PLUR, N2.PLUR, N2.PLUR],
        }

        # Inclusive valid spans (corresponding to the table above).
        self.spans = [(0, 0), (1, 1), (2, 2), (3, 29), (30, None)]

        # Check the config data.
        seen_inf = False
        for a, z in self.spans:
            assert 0 <= a
            assert 0 <= z or z is None
            if z == None:
                seen_inf = True
            else:
                assert a <= z
        assert seen_inf  # must cover all natural numbers.

        # Integer guesses (some are known/exact) (take the largest if overlap).
        self.guesses = [0, 1, 2, 15, 30, 30]
        for guess, span in zip(self.guesses, self.spans):
            if span[1] is None:
                assert span[0] <= guess
            else:
                assert span[0] <= guess <= span[1]

        # Comparison integers.  Where there is only one possible value, there is
        # one compint; where there are more, there are three to represent
        # lt/eq/gt comparisons.
        self.compint_groups = [(0,), (1,), (2,), (3, 4, 5), (6, 7, 8)]

        # Any nx -> indexes in spans list.
        nx2xx = defaultdict(list)
        for cols in self.class2col2nx.itervalues():
            for x, col in enumerate(cols):
                nx2xx[col].append(x)

        # Any nx -> NX to convert to -> nxs of that class.
        self.nx2class2nxs = defaultdict(dict)
        for nx in NX.values:
            for to_class in [N5, N3, N2]:
                to_ee = []
                for x in nx2xx[nx]:
                    to_ee.append(self.class2col2nx[to_class][x])
                self.nx2class2nxs[nx][to_class] = list(set(to_ee))

        # Any nx -> its natural number spans.
        self.nx2spans = {}
        for nx, xx in nx2xx.iteritems():
            self.nx2spans[nx] = reduce_spans(map(self.spans.__getitem__, xx))

        # Any nx -> whether exact (can be only one integer).
        self.nx2isexact = {}
        for nx, spans in self.nx2spans.iteritems():
            self.nx2isexact = (len(self.spans) == 1 and
                               self.spans[0][0] == self.spans[0][1])

        # Any nx -> guessed natural number value (some are exact).
        self.nx2guess = {}
        for nx, xx in nx2xx.iteritems():
            # take the largest, because as NX classes become larger and more
            # refined, the new divisions are on the small end.
            self.nx2guess[nx] = max(map(self.guesses.__getitem__, xx))

        # Any nx -> list of comparison ints.
        self.nx2compints = {}
        for nx, xx in nx2xx.iteritems():
            self.nx2compints[nx] = \
                sorted(reduce(lambda a, b: a + b,
                              map(self.compint_groups.__getitem__, xx)))

    # --------------------------------------------------------------------------
    # Conversion to integer.

    def to_int_spans(self, nx):
        return self.nx2spans[nx]

    def is_exact(self, nx):
        return self.nx2isexact[nx]

    def to_int(self, nx):
        return self.nx2guess[nx]

    # --------------------------------------------------------------------------
    # Conversion to NX.

    def _col_from_int(self, i):
        assert 0 <= i
        for x, span in enumerate(self.spans):
            if span[1] == -1:
                if span[0] <= i:
                    return x
            else:
                if span[0] <= i <= span[1]:
                    return x
        assert False  # Last one will be open-ended on right (None), so
                      # impossible.

    def int_to_nx(self, i, to_class):
        col = self._col_from_int(i)
        return self.class2col2nx[to_class][col]

    def nx_to_nxs(self, nx, to_class):
        return self.nx2class2nxs[nx][to_class]

    def nx_to_nx(self, nx, to_class):
        # Works always when convering to something broader, but only works for
        # certain inputs when converting narrower.
        ee = self.nx_to_nxs(nx, to_class)
        assert len(ee) == 1
        return ee[0]

    # --------------------------------------------------------------------------
    # NX-NX comparisons.

    def compints_from_nx(self, nx):
        return self.nx2compints[nx]

    def nx_lt_nx_is_possible(self, a, b):
        aa = self.nx2compints[a]
        bb = self.nx2compints[b]
        return aa[0] < bb[-1]

    def nx_lt_nx_is_guaranteed(self, a, b):
        aa = self.nx2compints[a]
        bb = self.nx2compints[b]
        return aa[-1] < bb[0]

    def nx_le_nx_is_possible(self, a, b):
        aa = self.nx2compints[a]
        bb = self.nx2compints[b]
        return aa[0] <= bb[-1]

    def nx_le_nx_is_guaranteed(self, a, b):
        aa = self.nx2compints[a]
        bb = self.nx2compints[b]
        return aa[-1] <= bb[0]

    def nx_eq_nx_is_possible(self, a, b):
        aa = self.nx2compints[a]
        bb = self.nx2compints[b]
        aa = set(aa)
        for b in bb:
            if b in aa:
                return True
        return False

    def nx_eq_nx_is_guaranteed(self, a, b):
        aa = self.nx2compints[a]
        bb = self.nx2compints[b]
        return len(aa) == 1 and aa == bb

    # --------------------------------------------------------------------------
    # NX-int comparisons.

    def compints_from_int(self, i):
        for x, span in enumerate(self.spans):
            if not (span[0] <= i <= span[1]):
                continue

            cc = self.compint_groups[x]
            if len(cc) == 1:
                return cc

            assert len(cc) == 3
            if i == span[0]:
                return cc[1:]
            elif i == span[1]:
                return cc[:-1]
            else:
                return cc

        assert False

    def nx_lt_int_is_possible(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return aa[0] < bb[-1]

    def nx_lt_int_is_guaranteed(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return aa[-1] < bb[0]

    def nx_le_int_is_possible(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return aa[0] <= bb[-1]

    def nx_le_int_is_guaranteed(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return aa[-1] <= bb[0]

    def nx_eq_nx_is_possible(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        aa = set(aa)
        for b in bb:
            if b in a:
                return True
        return False

    def nx_eq_nx_is_guaranteed(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.nx2compints[i]
        return len(aa) == 1 and aa == bb

    def nx_ge_int_is_possible(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return bb[0] <= aa[-1]

    def nx_ge_int_is_guaranteed(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return bb[-1] <= aa[0]

    def nx_gt_int_is_possible(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return bb[0] < aa[-1]

    def nx_gt_int_is_guaranteed(self, nx, i):
        aa = self.nx2compints[nx]
        bb = self.compints_from_int(i)
        return bb[-1] < aa[0]


_MGR = GrammaticalNumberManager()


def compints_from_nx(nx):
    return _MGR.compints_from_nx(nx)


def nx_to_nx(nx, klass):
    return _MGR.nx_to_nx(nx, klass)


def nx_to_nxs(nx, klass):
    return _MGR.nx_to_nxs(nx, klass)
