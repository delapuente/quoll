from quoll.preamble import *
from quoll.assertions import *

@qdef(adj=True, ctl=True)
def db_oracle(marked_qubit, db_register):
  if control(db_register.is_max_value()):
    X(marked_qubit)


@qdef(adj=True, ctl=True)
def uniform_superposition_oracle(db_register):
  map(H, db_register)


@qdef(adj=True, ctl=True)
def state_preparation_oracle(marked_qubit, db_register):
  uniform_superposition_oracle(db_register)
  db_oracle(marked_qubit, db_register)


@qdef(adj=True, ctl=True)
def reflect_marked(marked_qubit):
  import math
  R1(math.pi, marked_qubit)


def reflect_zero(db_register):
  map(X, db_register)
  Controlled[Z](db_register[1:], db_register[0])
  map(X, db_register)


def reflect_start(marked_qubit, db_register):
  Adjoint[state_preparation_oracle](marked_qubit, db_register)
  reflect_zero(marked_qubit + db_register)
  state_preparation_oracle(marked_qubit, db_register)


def quantum_search(iterations, marked_qubit, db_register):
  state_preparation_oracle(marked_qubit, db_register)
  for _ in range(iterations):
    reflect_marked(marked_qubit)
    reflect_start(marked_qubit, db_register)


def apply_quantum_search(iterations, db_qubits_count) -> Tuple[bool, int]:
  with allocate(1, db_qubits_count) as (marked_qubit, db_register):
    quantum_search(iterations, marked_qubit, db_register)
    result_success = measure(marked_qubit)
    result_element = measure(db_register)
    return bool(result_success), int(result_element)


def state_preparation_oracle_test():
  for db_size in range(1, 6):
    with allocate(1, db_size) as (marked_qubit, db_register):
      state_preparation_oracle(marked_qubit, db_register)
      success_amplitude = 1.0 / ((2**len(db_register)) ** 0.5)
      success_probability = success_amplitude ** 2
      assertProb(
        [measure(marked_qubit)], [True],
        prob=success_probability,
        msg="Error: Success probability does not match theory",
        delta=1E-1)


def grover_hard_coded_test():
  from math import sin, asin, sqrt

  for db_size in range(1, 5):
    for iterations in range(1, 6):
      with allocate(1, db_size) as (marked_qubit, db_register):
        quantum_search(iterations, marked_qubit, db_register)
        success_amplitude = sin(
          float(2 * iterations + 1) * asin(1.0 / sqrt(float(2 ** db_size))))
        success_probability = success_amplitude ** 2
        assertProb(
          [measure(marked_qubit)], [True],
          prob=success_probability,
          msg="Error: Success probability does not match theory",
          delta=1E-1)

        if measure(marked_qubit):
          assertFact(
            measure(db_register) == db_register.all_ones_value(),
            msg='Found state should be 1..1 string.')


def main():
  state_preparation_oracle_test()
  grover_hard_coded_test()
  print('Everything went fine.')


if __name__ == '__main__':
  main()
