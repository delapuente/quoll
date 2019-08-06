from typing import List, Tuple
from functools import partial

from quoll.preamble import *
from quoll.assertions import *

QRegister = List[Qubit]

@qasm(Adj, Ctl)
def db_oracle(marked_qubit: Qubit, db_register: QRegister):
  Controlled[X](db_register, marked_qubit)


@qasm(Adj, Ctl)
def uniform_superposition_oracle(db_register: QRegister):
  map(H, db_register)


@qasm(Adj, Ctl)
def state_preparation_oracle(marked_qubit: Qubit, db_register: QRegister):
  uniform_superposition_oracle(db_register)
  db_oracle(marked_qubit, db_register)


@qasm(Adj, Ctl)
def reflect_marked(marked_qubit: Qubit):
  import math
  R1(math.pi, marked_qubit)


def reflect_zero(db_register: QRegister) -> Unit:
  map(X, db_register)
  Controlled[Z](db_register[1:], db_register[0])
  map(X, db_register)


def reflect_start(marked_qubit: Qubit, db_register: QRegister):
  Adjoint[state_preparation_oracle](marked_qubit, db_register)
  reflect_zero([marked_qubit] + db_register)
  state_preparation_oracle(marked_qubit, db_register)


def quantum_search(iterations: int, marked_qubit: Qubit, db_register: QRegister):
  state_preparation_oracle(marked_qubit, db_register)
  for _ in range(iterations):
    reflect_marked(marked_qubit)
    reflect_start(marked_qubit, db_register)


def apply_quantum_search(iterations: int, db_qubits_count: int) -> Tuple[bool, int]:
  with allocate(1, db_qubits_count) as (marked_qubit, db_register):
    quantum_search(iterations, marked_qubit, db_register)
    result_success = measure(marked_qubit, reset=True)
    result_element = measure(db_register, reset=True)
    return bool(result_success), int(result_element)


def state_preparation_oracle_test():
  for db_size in range(6):
    with allocate(1, db_size) as (marked_qubit, db_register):
      state_preparation_oracle(marked_qubit, db_register)
      success_amplitude = 1.0 / ((2**db_register) ** 0.5)
      success_probability = success_amplitude ** 2
      assertProb(
        [measure(marked_qubit)], [True],
        prob=success_probability,
        msg="Error: Success probability does not match theory",
        delta=1E-10)


def grover_hard_coded_test():
  from math import sin, asin, sqrt

  for db_size in range(5):
    for iterations in range(6):
      with allocate(1, db_size) as (marked_qubit, db_register):
        quantum_search(iterations, marked_qubit, db_register)
        success_amplitude = sin(
          float(2 * iterations + 1) * asin(1.0 / sqrt(float(2 ** db_size))))
        success_probability = success_amplitude ** 2
        assertProb(
          [measure(marked_qubit)], [True],
          prob=success_probability,
          msg="Error: Success probability does not match theory",
          delta=1E-10)

        result = measure(marked_qubit)
        if result:
          results = [measure(q) for q in db_register]
          assertFact(
            all(results),
            msg='Found state should be 1..1 string.')


def main():
  state_preparation_oracle_test()
  grover_hard_coded_test()
  print('Everything went fine.')


if __name__ == '__main__':
  main()
