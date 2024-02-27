import yaml

from panoptes.agent.pzombie import PhilosophicalZombie


PRE = '\t\t\t[EVAL]'


def main():
    agent = PhilosophicalZombie()

    fn = 'tests/babi_like.yaml'
    jj = yaml.yaml_safe_load(open(fn))
    for j in jj:
        print(PRE, '-' * 80)
        agent.reset()
        uid = agent.new_user()
        name = j['name']
        print(PRE, name)
        for pair in j['pairs']:
            in_s = pair['in'].decode('utf-8')
            print(PRE, 'IN = (%s)' % in_s)

            want_out = pair.get('out')

            if want_out:
                want_out = want_out.decode('utf-8')
                print(PRE, 'WANT OUT = (%s)' % want_out)

            got_out = agent.put(uid, in_s).out
            if got_out:
                print(PRE, 'GOT OUT = (%s)' % got_out)

            try:
                assert want_out == got_out
            except:
                print(PRE, 'died', 'WANTED', want_out, '!=', 'GOT', got_out)
                raise


if __name__ == '__main__':
    main()
