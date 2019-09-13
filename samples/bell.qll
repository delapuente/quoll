from quoll.preamble import *
from quoll.assertions import *


@qasm(adj=True, ctl=True)
def bell_state(c, t):
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

def test_bell_state_adj():
 with allocate(1, 1) as (c, t):
    bell_state(c, t)
    Adjoint[bell_state](c, t)
    assertProb(
      [measure(t), measure(c)], [False, False],
      prob=1, msg='00 combination should be 100%.',
      delta=0
    )

def test_controlled_bell():
  with allocate(1, 1, 1) as (control, bell_control, bell_target):
    H(control)
    Controlled[bell_state](control, bell_control, bell_target)
    test_results = [
      ([False, False, False], 0.5),
      ([True, False, False], 0.25),
      ([True, True, True], 0.25)
    ]
    for pattern, prob in test_results:
      assertProb(
        [measure(control), measure(bell_control), measure(bell_target)],
        pattern, prob=prob,
        msg=f'${pattern} should happend with probability ${prob}.',
        delta=1E-7
      )

def main():
  test_bell_state()
  test_bell_state_adj()
  print('Everything is OK! Done.')

if __name__ == '__main__':
  main()