from quoll.preamble import *
from quoll.assertions import *

@qdef(adj=True, ctl=True)
def config_1010(a, b, c, d):
  # Hypothesis: a, b, c, d are sorted from min to max
  X(d)
  X(b)

def main():
  with allocate(1, 1, 1, 1) as (a, b, c, d):
    config_1010(a, b, c, d)
    assertProb(
      [measure(d), measure(c), measure(b), measure(a)],
      [True, False, True, False], prob=1
    )