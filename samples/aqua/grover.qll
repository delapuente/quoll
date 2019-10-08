from quoll.preamble import *
from quoll.assertions import *
import math

class Grover:

  def __init__(self, db_oracle, db_qubits_count):
    self._db_oracle = db_oracle
    self._db_qubits_count = db_qubits_count

  def run(self):
    iterations = math.ceil(math.pi/4 * (2**self._db_qubits_count)**.5)
    with allocate(1, self._db_qubits_count) as (marked_qubit, db_register):
      self._quantum_search(iterations, marked_qubit, db_register)
      result_success = measure(marked_qubit)
      result_element = measure(db_register)
      return bool(result_success), int(result_element)

  @qdef(adj=True, ctl=True)
  def _uniform_superposition_oracle(self, db_register):
    map(H, db_register)

  @qdef(adj=True, ctl=True)
  def _state_preparation_oracle(self, marked_qubit, db_register):
    self._uniform_superposition_oracle(db_register)
    self._db_oracle(marked_qubit, db_register)

  @qdef(adj=True, ctl=True)
  def _reflect_marked(self, marked_qubit):
    R1(math.pi, marked_qubit)

  def _reflect_zero(self, db_register):
    map(X, db_register)
    Controlled[Z](db_register[1:], db_register[0])
    map(X, db_register)

  def _reflect_start(self, marked_qubit, db_register):
    Adjoint[self._state_preparation_oracle](marked_qubit, db_register)
    self._reflect_zero(marked_qubit + db_register)
    self._state_preparation_oracle(marked_qubit, db_register)

  def _quantum_search(self, iterations, marked_qubit, db_register):
    self._state_preparation_oracle(marked_qubit, db_register)
    for _ in range(iterations):
      self._reflect_marked(marked_qubit)
      self._reflect_start(marked_qubit, db_register)