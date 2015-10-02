import os
import shutil

from panoptes.dataset.evaluator import Evaluator


class HtmlEvaluator(Evaluator):
    def dump_task_head(self, out):
        out.write("""
<html>
<head>
    <style type="text/css">
body {
    background: #ace;
}
#page {
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;
    margin-bottom: 100px;
    width: 800px;
    background: #bdf;
}
.episode {
    margin: 10px;
    padding: 10px;
}
.correct {
    background: white;
}
.wrong {
    background: #fdd;
}
    </style>
</head>
<body>
    <div id="page">
""")

    def dump_episode_head(self, episode_index, out):
        out.write("""
        <div class="episode">
""")

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
        self.dump_episode_head(episode_index, out)
        agent.reset()
        uid = agent.new_user()
        for in_s, want_out in episode.pairs:
            delib = agent.put(uid, in_s)
            line = '%d %d %d %s' % (
                len(delib.recognized.parses), len(delib.recognized.ssens),
                len(delib.recognized.dsens), in_s.encode('utf-8'))
            if want_out or delib.out:
                if want_out != delib.out:
                    line += ' want "%s" got "%s"' % (want_out, delib.out)
                    line = '<span class="wrong">%s</span>' % line
                else:
                    line += '"%s"' % want_out
                    line = '<span class="correct">%s</span>' % line
            line += '<br>\n'
            out.write(line)
        self.dump_episode_foot(out)

    def evaluate_task(self, agent, task, episodes_per_task, out):
        self.dump_task_head(out)
        if episodes_per_task is None:
            episodes = task.episodes
        else:
            episodes = task.episodes[:episodes_per_task]
        for i, episode in enumerate(episodes):
            self.evaluate_episode(agent, i, episode, out)
        self.dump_task_foot(out)

    def evaluate(self, agent, dataset, episodes_per_task=None):
        root = 'data/evaluation/%s/' % dataset.name
        if os.path.exists(root):
            shutil.rmtree(root)
        os.makedirs(root)
        print 'wtf', len(dataset.tasks)
        dataset.overview()
        for i, task in enumerate(dataset.tasks):
            fn = root + '%02d_%s.html' % (i + 1, task.name)
            with open(fn, 'wb') as out:
                self.evaluate_task(agent, task, episodes_per_task, out)
