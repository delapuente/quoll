import random

from quoll.preamble import *
from quoll.assertions import *

from samples.algorithms.utils import share_quantum_radio

class Alice:

  def __init__(self, q):
    self.q = q

  @qdef
  def encode(self, n):
    if n & 0b01:
      X(self.q)
    if n & 0b10:
      Z(self.q)

class Bob:

  def __init__(self, q):
    self.q = q

  def receive(self, sender_q):
    self._sender_q = sender_q

  @qdef
  def decode(self):
    Adjoint[share_quantum_radio](self._sender_q, self.q)

def main():
  with allocation(1, 1) as (q1, q2):
    share_quantum_radio(q1, q2)
    alice = Alice(q1)
    bob = Bob(q2)

    message = random.randrange(0, 3)
    alice.encode(message)

    bob.receive(alice.q)
    bob.decode()

    # TODO: This should be done as part of .decode() but currently, measure()
    # is only useful when used inside the allocation context's suite.
    assertProb([measure(bob.q + alice.q)], [message], 1.0)

  print(f'Message "{message}" was encoded and decoded successfully!')


if __name__ == '__main__':
  main()