from quoll.preamble import *
from quoll.assertions import *

# The boilerplate module includes the repetitive extra code needed for
# quoll code.
import quoll.boilerplate as bp

# Unit are translated to singleton callables.
@bp.singleton
class bell_state:

  def __call__(self, c, t):
    H(c)
    Controlled[X]([c], t)

  # Since this Unit is also Adj, __adj__ is automatically added.
  # The implementation is generated automatically from the definition.
  @property
  def __adj__(self):
    def _adjoint(c, t):
      Adjoint[Controlled[X]]([c], t)
      Adjoint[H](c)

    _adjoint.__adj__ = self
    return _adjoint

  @property
  def __ctl__(self):
    raise NotImplementedError

# Not a unit, so not translated, so far:
def test_bell_state():
  with reset(allocate(1, 1)) as (c, t):
    bell_state(c, t)
    # The static analisys conclude this is a valid program since:
    # 1. There is no further circuit alterations after measurements.
    # 2. There is no dynamic behaviour.
    #
    # So, all measurements get group and sorted.
    _mp_t = measure(t)
    _mp_c = measure(c)
    # And the circuit is executed. Arguments sorted by lexicographical order.
    _m_c, _m_t = bp.execute(_mp_c, _mp_t)

    result = _m_t
    assertProb(
      [_m_t, _m_c], [True, True],
      prob=0.5, msg='11 combination should be 50%.',
      delta=1E-1
    )
    assertProb(
      [_m_t, _m_c], [False, False],
      prob=0.5, msg='00 combination should be 50%.',
      delta=1E-1
    )
    print('Everything is OK! Done.')

if __name__ == '__main__':
  test_bell_state()