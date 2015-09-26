from panoptes.agent.pzombie import PhilosophicalZombie
from panoptes.dataset.babi import load_babi


def main():
    d = 'data/tasks_1-20_v1-2/en-10k/'
    babi = load_babi(d)
    agent = PhilosophicalZombie()
    uid = agent.new_user()
    while True:
        text = raw_input('> ')
        print agent.put(uid, text)


if __name__ == '__main__':
    main()
