import itertools
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
  total_registers = len(cregisters)
  untested_registers_count = total_registers - len(tested_registers)

  favorable = 0
  choice: List[Optional[str]] = [None] * total_registers
  for index, value in tested_registers:
    padding = cregisters[index].size
    choice[index] = bin(value)[2:].rjust(padding, '0') # Binary representation

  for one_choice in _expand_choices([*choice], cregisters):
    # TODO: choice is little-endian (we need big-endian). Qiskit doc is wrong.
    favorable += histogram.get(' '.join(reversed(one_choice)), 0)

  actual_probability = favorable / total
  actual_delta = abs(actual_probability - prob)

  assertion_message = f'Probabilities don\'t match (delta={actual_delta}).'
  if msg:
    assertion_message = f'{assertion_message}\n{msg}'

  assert actual_delta <= delta, assertion_message


def assertFact(fact, msg):
  assert fact, msg


# TODO: Handling undefined measurements can be a total waste in memory.
# I think we should work with integers and bit operations but let's see
# how this behaves so far.
def _expand_choices(choice, cregisters):
  undefined_positions = [
    (index, cregisters[index].size)
    for index, item in enumerate(choice) if item is None]

  undefined_qubits_count = sum(size for _, size in undefined_positions)
  undefined_combinations_count = 2**undefined_qubits_count
  for combination in range(undefined_combinations_count):
    yield _fill(
      choice, undefined_positions, combination, undefined_qubits_count)

def _fill(template, placeholders, combination, width):
  remaining_binarystring = bin(combination)[2:].rjust(width, '0')
  for index, size in placeholders:
    binarystring, remaining_binarystring = _take(remaining_binarystring, size)
    template[index] = binarystring

  return template

def _take(binarystring, size):
  return binarystring[:size], binarystring[size:]
