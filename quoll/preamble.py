from abc import ABC, abstractmethod, abstractproperty
from typing import Type, TypeVar, Generic, Iterable, List, Callable, Tuple, Sequence, MutableMapping
from functools import partial

from quoll.measurements import Measurement, MeasurementProxy
import quoll.boilerplate as bp

T = TypeVar('T')
P = TypeVar('P')

#TODO: This and other classes should be abstract class and the whole Qiskit
# implementation should be injected.
class Qubit:

  allocation: 'Allocation'

  register: bp.QuantumRegister

  def __init__(self, allocation: 'Allocation', register: bp.QuantumRegister):
    self.allocation = allocation
    self.register = register

  def __iter__(self):
    return iter(self.register)

  def __len__(self):
    return len(self.register)


class MetaFunctor(type):

  def __add__(self, another: 'MetaFunctor') -> 'MetaFunctor':
    pass


class Functor:
  pass

class Controlled(Functor, metaclass=MetaFunctor):

  #TODO: Add type annotation for operation.
  #TODO: Refine return type with structured typing if possible.
  def __class_getitem__(cls, operation) -> Callable:
    return operation.__ctl__

Ctl = Controlled

class Adjoint(Functor, metaclass=MetaFunctor):

  #TODO: Add type annotation for operation.
  #TODO: Refine return type with structured typing if possible.
  def __class_getitem__(cls, operation) -> Callable:
    return operation.__adj__

Adj = Adjoint


def X(q: Qubit):
  q.allocation.circuit.x(q.register)

def _X_ctl(control: Sequence[Qubit], q: Qubit):
  #TODO: Extend with toffoli gates to allow multi controlled X.
  #TODO: Provide a decorator for adding the proper runtime signature checks.
  if not len(control) or len(control) > 1:
    raise NotImplementedError(
      'Current Controlled[X] implementation supports one control qubit only')

  q.allocation.circuit.cx(control[0].register, q.register)

setattr(X, '__adj__', X)
setattr(X, '__ctl__', _X_ctl)
setattr(_X_ctl, '__adj__', _X_ctl)
#TODO: No idea of how to define the ctl of a ctl

def H(q: Qubit):
    q.allocation.circuit.h(q.register)

setattr(H, '__adj__', H)

def R1(angle: float, q: Qubit):
  pass

def Z(q: Qubit):
  pass

def head(l: list):
  return l[0]

def tail(l: list):
  return l[1:]

class Unit(Generic[T]):
  def __class_getitem__(cls, item):
    return True

class Allocation:

  circuit: bp.QuantumCircuit

  qubits: Tuple[Qubit, ...]

  def __init__(self, *sizes: int):
    registers = bp.new_registers(*sizes)
    circuit = bp.new_circuit_with_registers(registers)
    self.circuit = circuit
    self.qubits = tuple(map(partial(Qubit, self), registers))

  def __enter__(self):
    return self

  def __exit__(self, *_):
    pass

  def __iter__(self) -> Iterable[Qubit]:
    return iter(self.qubits)

def allocate(*sizes: int) -> Allocation:
  return Allocation(*sizes)


_MEASUREMENT_PROXY_CACHE: MutableMapping[Qubit, MeasurementProxy] = {}

def measure(register: Qubit, reset=False) -> MeasurementProxy:
  if not register in _MEASUREMENT_PROXY_CACHE:
    circuit = register.allocation.circuit
    cregister = bp.ClassicalRegister(len(register))
    qregister = register.register
    circuit.add_register(cregister)
    circuit.measure(qregister, cregister)
    _MEASUREMENT_PROXY_CACHE[register] = MeasurementProxy(circuit, qregister, cregister)

  return _MEASUREMENT_PROXY_CACHE[register]


class ResetContext:

  def __init__(self, allocation: Allocation):
    self._allocation = allocation

  def __enter__(self):
    return self._allocation.__enter__()

  def __exit__(self, *_):
    self._allocation.__exit__(*_)
    ... #TODO: Reset qubits of the allocation


def reset(allocation: Allocation) -> ResetContext:
  return ResetContext(allocation)


def qasm(*args, **kwargs):
  if len(args) == 1 and not len(kwargs) and callable(args[0]):
    return qasm()(args[0])

  def _decorator(item):
    return item

  return _decorator
