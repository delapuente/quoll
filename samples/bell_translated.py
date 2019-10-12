# The boilerplate module includes the repetitive extra code needed for
# quoll code.
import quoll.boilerplate as bp

from quoll.preamble import *
from quoll.assertions import *

# The decorator @qasm mark the implementation of a unitary.
# No parameters means nothing to autogenerate.
@qasm
def bell_state(c, t):
  H(c)
  Controlled[X]([c], t)


def _bell_state_adj(c, t):
  Adjoint[Controlled[X]]([c], t)
  Adjoint[H](c)


setattr(bell_state, '__adj__', _bell_state_adj)
setattr(_bell_state_adj, '__adj__', bell_state)

# Not a unit, so not translated, so far:
def test_bell_state():
  with allocation(1, 1) as (c, t):
    bell_state(c, t)
    # The static analisys conclude this is a valid program since:
    # 1. There is no further circuit alterations after measurements.
    # 2. There is no dynamic behaviour.
    #
    # So, all measurements get group and sorted.
    _mp1 = measure(t)
    _mp2 = measure(c)
    _mp3 = measure(t)
    _mp4 = measure(c)
    # And the circuit is executed. Arguments sorted by lexicographical order.
    _m1, _m2, _m3, _m4 = bp.execute(_mp1, _mp2, _mp3, _mp4)

    assertProb(
      [_m1, _m2], [True, True],
      prob=0.5, msg='11 combination should be 50%.',
      delta=1E-1
    )
    assertProb(
      [_m3, _m4], [False, False],
      prob=0.5, msg='00 combination should be 50%.',
      delta=1E-1
    )


def test_bell_state_adj():
 with allocation(1, 1) as (c, t):
    bell_state(c, t)
    Adjoint[bell_state](c, t)
    _mp1 = measure(t)
    _mp2 = measure(c)
    _m1, _m2 = bp.execute(_mp1, _mp2)
    assertProb(
      [_m1, _m2], [False, False],
      prob=1, msg='00 combination should be 100%.',
      delta=0
    )

def main():
  test_bell_state()
  test_bell_state_adj()
  print('Everything is OK! Done.')

if __name__ == '__main__':
  main()