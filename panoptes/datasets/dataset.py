from panoptes.agent import Agent


class Episode(object):
    """
    A single run of some input/output pairs against an Agent before resetting
    its state.
    """

    def __init__(self, pairs):
        self.pairs = pairs

    def evaluate(self, agent):
        """
        Agent -> (num correct tests, num tests)
        """
        correct = 0
        total = 0
        for in_s, out in self.pairs:
            got_out = agent.overhear(in_s)
            if out is not None:
                correct += out == got_out
                total += 1
        return correct, total


class Task(object):
    """
    A collection of Episodes that evaluate the performance of an Agent on the
    same kind of problem.
    """

    def __init__(self, name, episodes):
        self.name = name
        self.episodes = episodes

    def evaluate(self, agent):
        """
        Agent -> accuracy
        """
        correct = 0
        total = 0
        for episode in self.episodes:
            agent.reset()
            a, b = episode.evaluate(agent)
            correct += a
            total += b
        return float(correct) / total


class Dataset(object):
    """
    A runner that sees how an Agent performs on different Tasks.
    """

    def __init__(self, tasks):
        self.tasks = tasks

    def preview(self):
        z = max(map(lambda t: len(t.name), self.tasks))
        for task in self.tasks:
            print task.name.ljust(z), len(task.episodes)

    def evaluate(agent):
        names_accs = []
        for task in self.tasks:
            acc = task.evaluate(agent)
            names_accs.append((task.name, acc))

        z = max(map(len, zip(*names_accs)[0]))
        for task, acc in names_accs:
            print '%s %.3f' % (task.ljust(z), acc * 100)
