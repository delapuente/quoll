from typing import Union, Sequence, List, Optional, cast
from quoll.measurements import Measurement

AnyResult = Union[bool, int]

def assertProb(measurements: Sequence[Measurement], results: Sequence[bool], prob: float, msg: str = '', delta=1E-3):
  assert len(measurements) > 0 and len(results) > 0,\
    'Measurements and results length cannot be 0'

  assert len(measurements) == len(results),\
    'Measurements and results have different length.'

  histogram = measurements[0].result.get_counts()
  total = sum(histogram.values())

  circuit = measurements[0].proxy.circuit
  cregisters = circuit.cregs
  tested_registers = tuple(
    zip((cregisters.index(m.proxy.classical_register) for m in measurements), results))
  total_registers = len(circuit.cregs)
  untested_registers_count = total_registers - len(tested_registers)
  if untested_registers_count:
    #TODO: Renormalize for when not all the registers are tested
    raise NotImplementedError

  favorable = 0
  choice: List[Optional[str]] = [None] * total_registers
  for index, value in tested_registers:
    choice[index] = bin(value)[2:] # Binary representation

  # TODO: choice is little-endian (we need big-endian). Qiskit doc is wrong.
  favorable += histogram.get(' '.join(reversed(choice)), 0)
  actual_probability = favorable / total
  actual_delta = abs(actual_probability - prob)

  assertion_message = f'Probabilities don\'t match (delta={actual_delta}).'
  if msg:
    assertion_message = f'{assertion_message}\n{msg}'

  assert actual_delta <= delta, assertion_message


def assertFact(fact, msg):
  assert fact, msg