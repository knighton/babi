from ling.verb.conjugation import conjugations_from_file


def main():
    fn = 'config/conjugations.csv'
    cc = conjugations_from_file(fn)
    print len(cc)


if __name__ == '__main__':
    main()
