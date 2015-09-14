from panoptes.agent import Agent
from panoptes.datasets import get_problems


def main():
    d = 'data/tasks_1-20_v1-2/en/'
    problems = get_problems(d)
    problem = problems[1]
    in_s, want_out = problem[0]

    print 'EVENTUAL INPUT:', in_s

    ss = [
        u'I was seen by you.',
        u'I slept because I was tired.',
        u'Sandra got the football there.',
        u'I have been being been.',
        u"Don't you see?",
        u'I went to my home town.',
        u'I threw the ball to you.',
    ]

    ss = [
        u'Tim saw Tom.',
        u'I watched them.',
        u'I saw you.',
        u'I walked.',
        u'I walked the dog.',
    ]

    a = Agent()
    for s in ss:
        print
        print
        a.put(s)
        print
        print

    #got_out = a.put(in_s)
    #assert want_out == got_out


if __name__ == '__main__':
    main()
