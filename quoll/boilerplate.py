from functools import partial
from typing import Type, TypeVar, Any, Tuple, Iterable
from dataclasses import dataclass

import qiskit
from qiskit import QuantumRegister, QuantumCircuit, BasicAer, ClassicalRegister
from qiskit.circuit import Qubit

import quoll
import quoll.config
from quoll.measurements import Measurement, MeasurementProxy

T = TypeVar('T')

def singleton(cls: Type[T]) -> T:
  return cls()


def execute(*proxies: MeasurementProxy):
  assert len(proxies) > 0, 'No measurement proxies were provided.'
  circuit = proxies[0].circuit
  backend = quoll.config.get_backend()
  basis_gates = ['u1', 'u2', 'u3', 'cx', 'id']
  result = qiskit.execute(
    [circuit], backend=backend,
    shots=quoll.config.get_shots(),
    basis_gates=basis_gates).result()
  return tuple(map(partial(Measurement, result=result), proxies))

def new_circuit_with_registers(registers: Iterable[QuantumRegister]) -> QuantumCircuit:
  return QuantumCircuit(*registers)

def new_registers(*sizes) -> Tuple[QuantumRegister, ...]:
  return tuple(map(QuantumRegister, sizes))

def wire_functors(operation, adjoint=None, controlled=None, adjoint_controlled=None):
  if operation == adjoint and controlled and not adjoint_controlled:
    adjoint_controlled = controlled

  if adjoint:
    setattr(operation, '__adj__', adjoint)
    setattr(adjoint, '__adj__', operation)

  if controlled:
    setattr(operation, '__ctl__', controlled)
    setattr(controlled, '__ctl__', controlled)

  if controlled and adjoint:
    assert adjoint_controlled is not None, 'Missing implementation of adjoing controlled'
    setattr(adjoint, '__ctl__', adjoint_controlled)
    setattr(controlled, '__adj__', adjoint_controlled)