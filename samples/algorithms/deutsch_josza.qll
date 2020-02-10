import random

from quoll.preamble import *
from quoll.assertions import *

from samples.algorithms.utils import oracle

def create_function(input_width):
  is_balanced = bool(random.randint(0, 1))
  if not is_balanced:
    return constant_function(random.randint(0, 1)), False

  return balanced_function(random.randrange(0, input_width)), True

def constant_function(constant):
  @qdef
  def f(_input, output):
    if constant == 1:
      X(output)

  return f

def balanced_function(qbit_index):
  @qdef
  def f(input_, output):
    Controlled[X](input_[qbit_index], output)

  return f

@qdef
def preparation(feed):
  X(feed)
  H(feed)

def main():
  input_width = 2
  (f, is_balanced) = create_function(input_width)
  with allocation(input_width, 1) as (input_, result):
    H(input_)
    oracle(f, input_, preparation)
    H(input_)
    guess_is_balanced = bool(measure(input_))
    assert guess_is_balanced == is_balanced, f'Wrong guess! function was {is_balanced and "balanced" or "constant"}'


if __name__ == '__main__':
  main()