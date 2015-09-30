import sys

from panoptes.agent.pzombie import PhilosophicalZombie
from panoptes.dataset.babi import load_babi


def main():
    d = 'data/tasks_1-20_v1-2/en-10k/'
    babi = load_babi(d)
    babi.overview()
    babi.preview(5)
    agent = PhilosophicalZombie()
    babi.evaluate(agent, max_num_episodes=5, out=sys.stdout)


if __name__ == '__main__':
    main()
