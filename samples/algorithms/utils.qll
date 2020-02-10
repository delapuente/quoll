from quoll.preamble import *

@qdef(adj=True)
def share_quantum_radio(a, b):
  H(a)
  Controlled[X](a, b)

@qdef
def oracle(f, f_i, preprocess=None):
  with ancilla(1) as (feed,):
    if preprocess:
      preprocess(feed)

    f(f_i, feed)

  return feed