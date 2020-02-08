from dataclasses import dataclass, field
from typing import Tuple, Union

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.result import Result

import quoll.boilerplate as bp

@dataclass
class MeasurementProxy:

  circuit: QuantumCircuit

  quantum_register: QuantumRegister

  classical_register: ClassicalRegister

@dataclass
class Measurement:

  proxy: MeasurementProxy

  result: Result

  measurement_bitstring: int = field(init=False)

  def __post_init__(self):
    whole_memory_bitstring, _ = max(
      self.result.get_counts().items(), key=lambda item: item[1])

    # TODO: Endian mess. Should clarify this is this way and add some tests.
    registers_bitstrings = list(reversed(whole_memory_bitstring.split(' ')))
    self.measurement_bitstring = registers_bitstrings[
      bp.__ALLOCATIONS__[-1].circuit.cregs.index(self.proxy.classical_register)]

  def __int__(self):
    return int(self.measurement_bitstring, 2)

  def __bool__(self):
    return bool(int(self))

  def __eq__(self, another: object) -> bool:
    if isinstance(another, int):
      return int(self) == another

    if isinstance(another, bool):
      return bool(self) == another

    return super().__eq__(another)
