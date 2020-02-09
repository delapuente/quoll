from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import overload, Type, TypeVar, Generic, Iterable, List, Callable, Tuple, Sequence, MutableMapping, Union
from functools import partial, wraps
from itertools import chain, repeat
from contextlib import contextmanager

from quoll.measurements import Measurement, MeasurementProxy
import quoll.boilerplate as bp

T = TypeVar('T')
P = TypeVar('P')

def qdef(*args, **kwargs):
  if len(args) == 1 and not len(kwargs) and callable(args[0]):
    return qdef()(args[0])

  def _decorator(item):
    item.__isqdef__ = True
    return item

  return _decorator

#TODO: This and other classes should be abstract class and the whole Qiskit
# implementation should be injected.
class AllOneControl:
  def __init__(self, *values: 'Qubits'):
    assert len(values), 'At least one piece of data is needed to control upon it'
    self.values = values

  @overload
  def __and__(self, other: 'Qubits') -> 'AllOneControl': ...

  @overload
  def __and__(self, other: 'AllOneControl') -> 'AllOneControl': ...

  def __and__(self, other: Union['Qubits', 'AllOneControl']) -> 'AllOneControl':
    if not isinstance(other, AllOneControl):
      other = AllOneControl(other)
    return AllOneControl(*(*self.values, *other.values))


@dataclass
class QComparison:
  qubits: 'Qubits'

  integer: int

QiskitQubits = Union[bp.QuantumRegister, List[bp.Qubit]]


class Qubits:

  allocation: 'Allocation'

  qiskit_qubits: List[bp.Qubit]

  def __init__(self, allocation: 'Allocation', qiskit_qubits: QiskitQubits):
    self.allocation = allocation
    self.qiskit_qubits = [*qiskit_qubits]

  def __len__(self):
    return len(self.qiskit_qubits)

  def __getitem__(self, item):
    if not isinstance(item, slice):
      return Qubits(self.allocation, [self.qiskit_qubits[item]])

    return Qubits(self.allocation, self.qiskit_qubits[item])

  def __add__(self, more_data):
    return Qubits(
      self.allocation, [*self.qiskit_qubits, *more_data.qiskit_qubits])

  def __and__(self, other: 'Qubits') -> AllOneControl:
    return AllOneControl(self, other)

  def all_ones_value(self) -> int:
    return 2**len(self) - 1

  def is_max_value(self):
    return self == self.all_ones_value()

  def __eq__(self, another: object) -> Union[QComparison, bool]:
    # TODO: Add support for comparing two registers. May require extending
    # the allocation with ancilla. Should be transparent for the user.
    if isinstance(another, int):
      return QComparison(self, another)

    return super().__eq__(another)

class Functor:
  pass

class Controlled(Functor):

  #TODO: Add type annotation for operation.
  #TODO: Refine return type with structured typing if possible.
  def __class_getitem__(cls, operation) -> Callable:
    if not hasattr(operation, '__ctl__'):
      raise RuntimeError(f'Cannot get a controlled version of {operation}')
    if hasattr(operation, '__self__'):
      return getattr(operation.__self__, operation.__ctl__.__name__)
    return operation.__ctl__

class Adjoint(Functor):

  #TODO: Add type annotation for operation.
  #TODO: Refine return type with structured typing if possible.
  def __class_getitem__(cls, operation) -> Callable:
    if not hasattr(operation, '__adj__'):
      raise RuntimeError(f'Cannot get the adjoint version of {operation}')
    if hasattr(operation, '__self__'):
      return getattr(operation.__self__, operation.__adj__.__name__)
    return operation.__adj__

from qiskit.extensions.standard.x import XGate

@qdef
def X(q: Qubits):
  bp.__ALLOCATIONS__[-1].circuit.x(q.qiskit_qubits)

@qdef
def _X_ctl(control: Union[AllOneControl, Qubits], q: Qubits):
  #TODO: Provide a decorator for adding the proper runtime signature checks.
  _multiplexed_control(XGate(), control, q)

bp.wire_functors(X, X, _X_ctl)

from qiskit.extensions.standard.h import HGate

@qdef
def H(q: Qubits):
    bp.__ALLOCATIONS__[-1].circuit.h(q.qiskit_qubits)

@qdef
def _H_ctl(control: Union[AllOneControl, Qubits], q: Qubits):
  #TODO: Provide a decorator for adding the proper runtime signature checks.
  _multiplexed_control(HGate(), control, q)

bp.wire_functors(H, H, _H_ctl)

from qiskit.extensions.standard.u1 import U1Gate

@qdef
def R1(angle: float, q: Qubits):
  bp.__ALLOCATIONS__[-1].circuit.u1(angle, q.qiskit_qubits)

@qdef
def _R1_adj(angle: float, q: Qubits):
  bp.__ALLOCATIONS__[-1].circuit.append(U1Gate(angle).inverse(), [q.qiskit_qubits])

@qdef
def _R1_adj_ctl(control: Union[AllOneControl, Qubits], angle: float, q: Qubits):
  _multiplexed_control(U1Gate(angle).inverse(), control, q)

@qdef
def _R1_ctl(control: Union[AllOneControl, Qubits], angle: float, q: Qubits):
  _multiplexed_control(U1Gate(angle), control, q)

bp.wire_functors(R1, _R1_adj, _R1_ctl, _R1_adj_ctl)

from qiskit.extensions.standard.z import ZGate

@qdef
def Z(q: Qubits):
  bp.__ALLOCATIONS__[-1].circuit.z(q.qiskit_qubits)

@qdef
def _Z_ctl(control: Union[AllOneControl, Qubits], q: Qubits):
  _multiplexed_control(ZGate(), control, q)

bp.wire_functors(Z, Z, _Z_ctl)

from qiskit.extensions.standard.rx import RXGate

@qdef
def RX(theta: float, q: Qubits):
  bp.__ALLOCATIONS__[-1].circuit.rx(theta, q.qiskit_qubits)

@qdef
def _RX_adj(theta: float, q: Qubits):
  bp.__ALLOCATIONS__[-1].circuit.append(RXGate(theta).inverse(), [q.qiskit_qubits])

@qdef
def _RX_ctl(control: Union[AllOneControl, Qubits], angle: float, q: Qubits):
  _multiplexed_control(RXGate(angle), control, q)

def _RX_adj_ctl(control: Union[AllOneControl, Qubits], angle: float, q: Qubits):
  _multiplexed_control(RXGate(angle).inverse(), control, q)

bp.wire_functors(RX, _RX_adj, _RX_ctl, _RX_adj_ctl)

from qiskit.extensions.standard.iden import IdGate
from qiskit.extensions.quantum_initializer.ucg import UCG

def _multiplexed_control(gate, control: Union[AllOneControl, Qubits], target: Qubits):
  # TODO: Now not considering the order because this is being controlled by
  # the all 1s sequence.
  if isinstance(control, Qubits):
    control = AllOneControl(control)

  control_qubits = tuple(chain(
    *(value.qiskit_qubits for value in control.values)))
  control_patterns_count = 2 ** len(control_qubits)
  gate_list = [
    IdGate().to_matrix()
    for _ in range(control_patterns_count - 1)] + [gate.to_matrix()]
  bp.__ALLOCATIONS__[-1].circuit.append(
    UCG(gate_list, False), (target.qiskit_qubits, ) + control_qubits)

def head(l: list):
  return l[0]

def tail(l: list):
  return l[1:]

class Unit(Generic[T]):
  def __class_getitem__(cls, item):
    return True

class Allocation:

  circuit: bp.QuantumCircuit

  qubits: Tuple[Qubits, ...]

  def __init__(self, *sizes: int):
    registers = bp.new_registers(*sizes)
    circuit = bp.new_circuit_with_registers(registers)
    self.circuit = circuit
    self.qubits = tuple(map(partial(Qubits, self), registers))

  def __enter__(self):
    bp.__ALLOCATIONS__.append(self)
    return self

  def __exit__(self, *_):
    bp.__ALLOCATIONS__.pop()

  def __iter__(self) -> Iterable[Qubits]:
    return iter(self.qubits)


# TODO: Should allow for managing and **reusing** ancilla qubits.
class AncillaExtension:

  allocation: Allocation

  qubits: Tuple[Qubits, ...]

  def __init__(self, allocation: Allocation, *sizes: int):
    registers = bp.new_registers(*sizes)
    allocation.circuit.add_register(*registers)
    self.allocation = allocation
    self.qubits = tuple(map(partial(Qubits, self), registers))

  def __enter__(self):
    return self

  def __exit__(self, *_):
    # TODO: Add an option for resetting the qubits. Tracking these and returning
    # them enables reusing. Not sure if adding this or let the compiler to take
    # care.
    pass

  def __iter__(self) -> Iterable[Qubits]:
    return iter(self.qubits)

def allocation(*sizes: int) -> Allocation:
  return Allocation(*sizes)

def ancilla(*sizes: int) -> AncillaExtension:
  return AncillaExtension(bp.__ALLOCATIONS__[-1], *sizes)

_MEASUREMENT_PROXY_CACHE: MutableMapping[object, MeasurementProxy] = {}

def measure(register: Qubits, reset=False) -> MeasurementProxy:
  if isinstance(register, Allocation):
    register = sum((r for r in register), Qubits(register, []))
  key = (*register.qiskit_qubits,)
  if not key in _MEASUREMENT_PROXY_CACHE:
    circuit = bp.__ALLOCATIONS__[-1].circuit
    cregister = bp.ClassicalRegister(len(register))
    qregister = register.qiskit_qubits
    circuit.add_register(cregister)
    circuit.measure(qregister, cregister)
    _MEASUREMENT_PROXY_CACHE[key] = MeasurementProxy(circuit, qregister, cregister)

  return _MEASUREMENT_PROXY_CACHE[key]


# TODO: Reinterpreted Python builtins
_PYTHON_MAP = map

@qdef
def map(f, *iterables):
  if not getattr(f, '__isqdef__', False):
    return _PYTHON_MAP(f, *iterables)

  list(_PYTHON_MAP(f, *iterables))

@qdef
def _map_adj(f, *iterables):
  list(_PYTHON_MAP(Adjoint[f], *iterables))

@qdef
def _map_ctl(control, f, *iterables):
  list(_PYTHON_MAP(Controlled[f], repeat(control), *iterables))

@qdef
def _map_adj_ctl(control, f, *iterables):
  list(_PYTHON_MAP(Adjoint[Controlled[f]], repeat(control), *iterables))

bp.wire_functors(map, _map_adj, _map_ctl, _map_adj_ctl)

@qdef
@contextmanager
def superposition(comp: QComparison):
  yield from _map_on_zero_valued_indices(X, comp)

@qdef
@contextmanager
def _superposition_ctl(control: Qubits, comp: QComparison):
  yield from _map_on_zero_valued_indices(partial(X.__ctl__, control), comp)

bp.wire_functors(superposition, superposition, _superposition_ctl)

def _map_on_zero_valued_indices(gate, comp: QComparison):
  qubits = comp.qubits
  int_binarystring = bin(comp.integer)[2:].rjust(len(qubits), '0')
  for stage in ['enter', 'exit']:
    # set/unset anticontrols
    for index, char in enumerate(reversed(int_binarystring)):
      if char == '0':
        gate(qubits[index])

    if stage == 'enter':
      yield qubits