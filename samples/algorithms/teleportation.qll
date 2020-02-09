from quoll.preamble import *
from quoll.assertions import *

from samples.algorithms.utils import share_quantum_radio

@qdef
def set_secret_state(target):
  import random
  from math import cos, pi
  angle = random.random() * pi/2.0
  RX(angle, target)
  chance = cos(angle/2.0)**2.0
  return chance

@qdef
def teleport(owner, target, receptor):
  Controlled[X](target, owner)
  H(target)

  Controlled[X](owner,receptor)
  Controlled[Z](target, receptor)
  measure(owner)
  measure(target)

def main():
  with allocation(1, 1, 1) as (alice, bob, original):
    chance_of_zero = set_secret_state(original)
    share_quantum_radio(alice, bob)
    teleport(alice, original, bob)
    assertProb([measure(bob)], [0], chance_of_zero)
    print('Bame me up, Scotty!')


if __name__ == '__main__':
  main()