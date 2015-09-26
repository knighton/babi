from panoptes.dataset.babi import load_babi


def main():
    d = 'data/tasks_1-20_v1-2/en-10k/'
    babi = load_babi(d)
    babi.preview()
    babi.overview()
    print babi


if __name__ == '__main__':
    main()
