from quoll.preamble import *
from quoll.assertions import *


def bell_state(c: Qubit, t: Qubit) -> Unit[Adj]:
  H(c)
  Controlled[X]([c], t)


def test_bell_state():
  with reset(allocate(1, 1)) as (c, t):
    bell_state(c, t)
    result = measure(t)
    assertProb(
      [measure(t), measure(c)], [True, True],
      prob=0.5, msg='11 combination should be 50%.'
    )
    assertProb(
      [measure(t), measure(c)], [False, False],
      prob=0.5, msg='00 combination should be 50%.'
    )
    print('Everything is OK! Done.')

if __name__ == '__main__':
  test_bell_state()