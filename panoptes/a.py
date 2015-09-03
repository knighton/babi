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
    s, want_out = problem[0]

    a = Agent()
    got_out = a.put(s)
    assert want_out == got_out


if __name__ == '__main__':
    main()
