from ling.verb.conjugation import conjugations_from_file, Conjugator
from ling.verb.verb_parser import VerbParser
from ling.verb.verb_sayer import VerbSayer


def main():
    fn = 'config/conjugations.csv'
    cc = conjugations_from_file(fn)
    print len(cc)
    conj = Conjugator(cc)
    print conj.identify_word('batting')
    print conj.identify_word('bat')
    print conj.identify_word('bats')
    print conj.identify_word('lose')

    verb_sayer = VerbSayer(conj)
    verb_parser = VerbParser.construct(verb_sayer, 'wut.pkl')


if __name__ == '__main__':
    main()
