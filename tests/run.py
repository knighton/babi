from panoptes.agent import Agent
from panoptes.datasets import get_problems


def main():
    d = 'data/tasks_1-20_v1-2/en/'
    problems = get_problems(d)
    problem = problems[1]
    in_s, want_out = problem[0]

    print('EVENTUAL INPUT:', in_s)

    ss = [
        'I was seen by you.',
        'I slept because I was tired.',
        'Sandra got the football there.',
        'I have been being been.',
        "Don't you see?",
        'I went to my home town.',
        'I threw the ball to you.',
    ]

    ss = [
        'Tim saw Tom.',
        'I watched them.',
        'I saw you.',
        'I walked.',
        'I walked the dog.',
    ]

    a = Agent()
    for s in ss:
        print()
        print()
        a.put(s)
        print()
        print()

    #got_out = a.put(in_s)
    #assert want_out == got_out


if __name__ == '__main__':
    main()
