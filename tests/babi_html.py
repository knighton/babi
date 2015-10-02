from panoptes.agent.pzombie import PhilosophicalZombie
from panoptes.dataset.babi import load_babi
from panoptes.dataset.html_evaluator import HtmlEvaluator


def main():
    agent = PhilosophicalZombie()

    d = 'data/tasks_1-20_v1-2/en-10k/'
    babi = load_babi(d)

    ev = HtmlEvaluator()

    ev.evaluate(agent, babi, episodes_per_task=None)


if __name__ == '__main__':
    main()
