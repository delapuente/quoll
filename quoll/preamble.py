from abc import ABC, abstractmethod, abstractproperty
from typing import Type, TypeVar, Generic, Iterable, List, Callable, Tuple, Sequence
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


@bp.singleton
class X:

  def __call__(self, q: Qubit):
    q.allocation.circuit.x(q.register)

  #TODO: Provide the means for setting up...
  #TODO:   The adjoint and controlled versions of __adj__ and __ctl__.
  @property
  def __ctl__(self):

    #TODO: Provide a decorator for adding the proper runtime signature checks.
    def _controlled(control: Sequence[Qubit], q: Qubit):
      #TODO: Extend with toffoli gates to allow multi controlled X.
      if not len(control) or len(control) > 1:
        raise NotImplementedError(
          'Current Controlled[X] implementation supports one control qubit only')

      q.allocation.circuit.cx(control[0].register, q.register)

    return _controlled

  @property
  def __adj__(self):
    return self


@bp.singleton
class H:

  def __call__(self, q: Qubit):
    q.allocation.circuit.h(q.register)

  @property
  def __ctl__(self):
    raise NotImplementedError

  @property
  def __adj__(self):
    return self

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


def measure(register: Qubit, reset=False) -> MeasurementProxy:
  #TODO: Keep a cache for returning the same MeasurementProxy for the same Qubit
  circuit = register.allocation.circuit
  cregister = bp.ClassicalRegister(len(register))
  qregister = register.register
  circuit.add_register(cregister)
  circuit.measure(qregister, cregister)
  return MeasurementProxy(circuit, qregister, cregister)


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