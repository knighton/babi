from agent import Agent
from datasets import get_problems
from ling.verb.verb_manager import VerbManager


def main():
    conj_f = 'config/conjugations.csv'
    verb_f = '../data/verbs.json'
    verb_mgr = VerbManager.from_files(conj_f, verb_f)

    d = '../data/tasks_1-20_v1-2/en/'
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
    ]

    a = Agent()
    for s in ss:
        a.put(s)

    #got_out = a.put(in_s)
    #assert want_out == got_out


if __name__ == '__main__':
    main()
