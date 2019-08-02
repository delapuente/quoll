from functools import partial
from typing import Type, TypeVar, Any, Tuple, Iterable
from dataclasses import dataclass

import qiskit
from qiskit import QuantumRegister, QuantumCircuit, BasicAer, ClassicalRegister

from quoll.measurements import Measurement, MeasurementProxy

T = TypeVar('T')

def singleton(cls: Type[T]) -> T:
  return cls()


def execute(*proxies: MeasurementProxy):
  assert len(proxies) > 0, 'No measurement proxies were provided.'
  circuit = proxies[0].circuit
  backend = get_backend()
  result = qiskit.execute([circuit], backend=backend).result()
  return tuple(map(partial(Measurement, result=result), proxies))

def new_circuit_with_registers(registers: Iterable[QuantumRegister]) -> QuantumCircuit:
  return QuantumCircuit(*registers)

def new_registers(*sizes) -> Tuple[QuantumRegister, ...]:
  return tuple(map(QuantumRegister, sizes))

#TODO: Make it configurable by quoll CLI.
def get_backend():
  return BasicAer.get_backend('qasm_simulator')