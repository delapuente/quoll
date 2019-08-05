from quoll.preamble import *
from quoll.assertions import *


@qasm
def bell_state(c: Qubit, t: Qubit):
  H(c)
  Controlled[X]([c], t)


def test_bell_state():
  with allocate(1, 1) as (c, t):
    bell_state(c, t)
    assertProb(
      [measure(t), measure(c)], [True, True],
      prob=0.5, msg='11 combination should be 50%.',
      delta=1E-1
    )
    assertProb(
      [measure(t), measure(c)], [False, False],
      prob=0.5, msg='00 combination should be 50%.',
      delta=1E-1
    )
    print('Everything is OK! Done.')


def main():
  test_bell_state()

if __name__ == '__main__':
  main()