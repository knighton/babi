from collections import defaultdict


class Episode(object):
    """
    A single run of some input/output pairs against an Agent before resetting
    its state.
    """

    def __init__(self, pairs):
        self.pairs = pairs

    def show(self):
        for in_s, out in self.pairs:
            print '    %s' % in_s.encode('utf-8')
            if out:
                print '        > %s' % out.encode('utf-8')

    def evaluate(self, agent, uid):
        """
        Agent -> (num correct tests, num tests, list of Deliberation)
        """
        print '\t\t\tEVAL' + '-' * 80
        correct = 0
        total = 0
        delibs = []
        for in_s, expect_out in self.pairs:
            print '\t\t\tEVAL INPUT:', in_s
            delib = agent.put(uid, in_s)
            delibs.append(delib)
            if expect_out:
                print '\t\t\tEVAL EXPECTED OUTPUT: (%s)' % expect_out
            if delib.out:
                print '\t\t\tEVAL GOT OUTPUT: (%s)' % delib.out
            if expect_out is not None:
                correct += expect_out == delib.out
                total += 1
                # assert expect_out == delib.out
        return correct, total, delibs


class Task(object):
    """
    A collection of Episodes that evaluate the performance of an Agent on the
    same kind of problem.
    """

    def __init__(self, name, episodes):
        self.name = name
        self.episodes = episodes

    def overview(self):
        num_ins = 0
        num_outs = 0
        for e in self.episodes:
            ins, outs = zip(*e.pairs)
            num_ins += len(ins)
            num_outs += len(filter(bool, outs))
        return self.name, len(self.episodes), num_ins, num_outs

    def preview(self, task_index, num_episodes_to_show):
        print
        print '  %d. %s:' % (task_index, self.name.encode('utf-8'))
        print
        for e in self.episodes[:num_episodes_to_show]:
            print
            e.show()

    def evaluate(self, agent, max_num_episodes):
        """
        Agent -> accuracy, list of stats
        """
        correct = 0
        total = 0
        delibs = []
        for i, episode in enumerate(self.episodes):
            if i == max_num_episodes:
                break
            agent.reset()
            uid = agent.new_user()
            a, b, sub_delibs = episode.evaluate(agent, uid)
            correct += a
            total += b
            delibs += sub_delibs
        return float(correct) / total, delibs


def distribution(nn):
    d = defaultdict(int)
    for n in nn:
        d[n] += 1
    rr = []
    for n in sorted(d):
        c = d[n]
        rr.append((n, c))
    return rr


class Dataset(object):
    """
    A runner that sees how an Agent performs on different Tasks.
    """

    def __init__(self, name, tasks):
        self.name = name
        self.tasks = tasks

    def overview(self):
        sss = [('#', 'task', 'episodes', 'inputs', 'questions')]
        for i, task in enumerate(self.tasks):
            ss = map(str, [i + 1] + list(task.overview()))
            sss.append(ss)
        zz = map(lambda aa: max(map(len, aa)), zip(*sss))
        for ss in sss:
            for i, s in enumerate(ss):
                z = zz[i]
                if i == 1:
                    s = s.ljust(z)
                else:
                    s = s.rjust(z)
                print s,
            print

    def preview(self, num_episodes_to_show=1):
        print 'Preview of %s:' % self.name.encode('utf-8')
        for i, task in enumerate(self.tasks):
            task.preview(i + 1, num_episodes_to_show)

    def evaluate(self, agent, max_num_episodes=None, out=None):
        accs = []
        delibs_per_task = []
        for i, task in enumerate(self.tasks):
            if i < 0:
                continue
            acc, delibs = task.evaluate(agent, max_num_episodes)
            accs.append(acc)
            delibs_per_task.append(delibs)

        if out:
            names = map(lambda t: t.name, self.tasks)

            for name, acc, delibs in zip(names, accs, delibs_per_task):
                line = '-- %s (%.3f%%)\n' % (name, acc * 100.0)
                out.write(line)

                parses = []
                ssens = []
                dsens = []
                for d in delibs:
                    parses.append(len(d.recognized.parses))
                    ssens.append(len(d.recognized.ssens))
                    dsens.append(len(d.recognized.dsens))

                out.write('   * parse\n')
                for length, count in distribution(parses):
                    line = '     * %d (%d)\n' % (length, count)
                    out.write(line)

                out.write('   * surface\n')
                for length, count in distribution(ssens):
                    line = '     * %d (%d)\n' % (length, count)
                    out.write(line)

                out.write('   * deep\n')
                for length, count in distribution(dsens):
                    line = '     * %d (%d)\n' % (length, count)
                    out.write(line)

        return float(sum(accs)) / len(accs)
