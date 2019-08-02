from typing import Union, Sequence, List, Optional, cast
from quoll.measurements import Measurement

AnyResult = Union[bool, int]

def assertProb(measurements: Sequence[Measurement], results: Sequence[bool], prob: float, msg: str, delta=1E-3):
  assert len(measurements) > 0 and len(results) > 0,\
    'Measurements and results length cannot be 0'

  #TODO: Add support for multi qubit registers
  assert len(measurements) == len(results),\
    'Measurements and results have different length.'

  histogram = measurements[0].result.get_counts()
  total = sum(histogram.values())

  circuit = measurements[0].proxy.circuit
  qregisters = circuit.qregs
  fixed_indices = tuple(
    zip((qregisters.index(m.proxy.quantum_register) for m in measurements), results))
  qubit_count = sum(map(len, circuit.qregs))
  free_indices_count = qubit_count - len(fixed_indices)
  if free_indices_count:
    #TODO: Do something here
    raise NotImplementedError

  favorable = 0
  choice: List[Optional[str]] = [None] * qubit_count
  for index, value in fixed_indices:
    choice[index] = '1' if value else '0'

  favorable += histogram.get(' '.join(choice), 0)
  actual_probability = favorable / total
  actual_delta = abs(actual_probability - prob)
  assert actual_delta < delta, f'Probabilities don\'t match (delta={actual_delta}).'


def assertFact(fact, msg):
  assert fact, msg