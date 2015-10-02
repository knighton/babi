import os
import shutil

from panoptes.dataset.evaluator import Evaluator


class HtmlEvaluator(Evaluator):
    def dump_overview_head(self, out):
        out.write("""
<html>
<head>
    <style type="text/css">
body {
    background: #69c;
}
#page {
    padding: 10px;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;
    margin-bottom: 100px;
    width: 800px;
}
.episode {
    margin: 10px;
    padding: 10px;
    background: #def;
    border: 2px solid white;
    border-radius: 2px;
}
.episode_title {
    font-weight: bold;
    width: 100%;
    text-align: center;
}
td {
    padding: 5px;
}
    </style>
</head>
<body>
    <div id="page">
        <div class="episode">
            <div class="episode_title">Overview</div>
""".strip())

    def dump_overview_foot(self, out):
        out.write("""
        </div>
    </div>
</body>
</html>
""".strip())

    def dump_task_head(self, out):
        out.write("""
<html>
<head>
    <style type="text/css">
body {
    background: #69c;
}
#page {
    padding: 10px;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;
    margin-bottom: 100px;
    width: 800px;
}
.episode {
    margin: 10px;
    padding: 10px;
    background: #def;
    border: 2px solid white;
    border-radius: 2px;
}
.episode_title {
    font-weight: bold;
    width: 100%;
    text-align: center;
}
.correct {
    background: #8f8;
}
.wrong {
    background: #fcc;
}
    </style>
</head>
<body>
    <div id="page">
""".strip())

    def dump_episode_head(self, episode_index, correct, total, out):
        out.write("""
        <div class="episode">
            <div class="episode_title">Episode %d (%d / %d)</div>
""" % (episode_index + 1, correct, total))

    def dump_episode_foot(self, out):
        out.write("""
        </div>
""")

    def dump_task_foot(self, out):
        out.write("""
    </div>
</body>
</html>
""")

    def evaluate_episode(self, agent, episode_index, episode, out):
        correct = 0
        total = 0
        agent.reset()
        uid = agent.new_user()
        lines = []
        for in_s, want_out in episode.pairs:
            delib = agent.put(uid, in_s)
            line = '%d %d %d %s ' % (
                len(delib.recognized.parses), len(delib.recognized.ssens),
                len(delib.recognized.dsens), in_s.encode('utf-8'))
            if want_out or delib.out:
                if want_out == delib.out:
                    line += '"%s"' % want_out
                    line = '<span class="correct">%s</span>' % line
                    correct += 1
                else:
                    line += 'want "%s" got "%s"' % (want_out, delib.out)
                    line = '<span class="wrong">%s</span>' % line
                total += 1
            line += '<br>\n'
            lines.append(line)

        self.dump_episode_head(episode_index, correct, total, out)

        for line in lines:
            out.write(line)

        self.dump_episode_foot(out)

        return correct, total

    def evaluate_task(self, agent, task, episodes_per_task, out):
        try:
            self.dump_task_head(out)
            if episodes_per_task is None:
                episodes = task.episodes
            else:
                episodes = task.episodes[:episodes_per_task]
            correct = 0
            total = 0
            for i, episode in enumerate(episodes):
                sub_correct, sub_total = \
                    self.evaluate_episode(agent, i, episode, out)
                correct += sub_correct
                total += sub_total
            self.dump_task_foot(out)
            return correct, total
        except:
            return 0, 1

    def evaluate(self, agent, dataset, episodes_per_task=None):
        root = 'data/evaluation/%s/' % dataset.name
        if os.path.exists(root):
            shutil.rmtree(root)
        os.makedirs(root)
        dataset.overview()
        results = []
        for i, task in enumerate(dataset.tasks):
            fn = root + '%02d_%s.html' % (i + 1, task.name)
            with open(fn, 'wb') as out:
                correct, total = \
                    self.evaluate_task(agent, task, episodes_per_task, out)
                results.append((correct, total))

        fn = root + 'overview.html'
        with open(fn, 'wb') as out:
            self.dump_overview_head(out)
            out.write('<table>')
            for i, ((correct, total), task) in \
                    enumerate(zip(results, dataset.tasks)):
                pct = 100.0 * correct / total
                line = """
                    <tr>
                        <td style="text-align: right">%d.</td>
                        <td style="text-align: right">%.2f%%</td>
                        <td style="text-align: right">%d</td>
                        <td style="text-align: right">%d</td>
                        <td>%s</td>
                    </tr>
                """ % (i + 1, pct, correct, total, task.name)
                out.write(line)
            out.write('</table>')
            self.dump_overview_foot(out)
