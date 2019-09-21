from quoll.preamble import *
from quoll.assertions import *
import math

_DB_ORACLE = None

@qdef(adj=True, ctl=True)
def _uniform_superposition_oracle(db_register):
  map(H, db_register)


@qdef(adj=True, ctl=True)
def _state_preparation_oracle(marked_qubit, db_register):
  _uniform_superposition_oracle(db_register)
  _DB_ORACLE(marked_qubit, db_register)


@qdef(adj=True, ctl=True)
def _reflect_marked(marked_qubit):
  import math
  R1(math.pi, marked_qubit)


def _reflect_zero(db_register):
  map(X, db_register)
  Controlled[Z](db_register[1:], db_register[0])
  map(X, db_register)


def _reflect_start(marked_qubit, db_register):
  Adjoint[_state_preparation_oracle](marked_qubit, db_register)
  _reflect_zero(marked_qubit + db_register)
  _state_preparation_oracle(marked_qubit, db_register)


def _quantum_search(iterations, marked_qubit, db_register):
  _state_preparation_oracle(marked_qubit, db_register)
  for _ in range(iterations):
    _reflect_marked(marked_qubit)
    _reflect_start(marked_qubit, db_register)


def grover(db_oracle, db_qubits_count) -> Tuple[bool, int]:
  global _DB_ORACLE
  _DB_ORACLE = db_oracle
  iterations = math.ceil(math.pi/4 * (2**db_qubits_count)**.5)
  with allocate(1, db_qubits_count) as (marked_qubit, db_register):
    _quantum_search(iterations, marked_qubit, db_register)
    result_success = measure(marked_qubit)
    result_element = measure(db_register)
    return bool(result_success), int(result_element)