from quoll.preamble import *

@qdef(adj=True)
def share_quantum_radio(a, b):
  H(a)
  Controlled[X](a, b)