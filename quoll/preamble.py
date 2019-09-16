from abc import ABC, abstractmethod, abstractproperty
from typing import Type, TypeVar, Generic, Iterable, List, Callable, Tuple, Sequence, MutableMapping, Union
from functools import partial
from itertools import chain

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
  def __init__(self, *values: 'QData'):
    assert len(values), 'At least one piece of data is needed to control upon it'
    self.values = values

  def __and__(self, other: 'QData'): ...
  def __and__(self, other: 'AllOneControl'):
    if not isinstance(other, AllOneControl):
      other = AllOneControl(other)
    return AllOneControl(*(*self.values, *other.values))

# TODO: This is actually a qubit stream. To be Python consistent, let's change
# the name to qubits (as in bytes approx.). All other high level values should
# be built on qubit streams by composition.
QiskitQubits = Union[bp.QuantumRegister, List[bp.Qubit]]

class QData:

  allocation: 'Allocation'

  qiskit_qubits: QiskitQubits

  def __init__(self, allocation: 'Allocation', qiskit_qubits: QiskitQubits):
    self.allocation = allocation
    self.qiskit_qubits = qiskit_qubits

  def __iter__(self):
    return iter(self.qiskit_qubits)

  def __len__(self):
    return len(self.qiskit_qubits)

  def __getitem__(self, item):
    if not isinstance(item, slice):
      return QData(self.allocation, [self.qiskit_qubits[item]])

    return QData(self.allocation, self.qiskit_qubits[item])

  def __add__(self, more_data):
    return QData(
      self.allocation, [*self.qiskit_qubits, *more_data.qiskit_qubits])

  def __and__(self, other: 'QData') -> AllOneControl:
    return AllOneControl(self, other)


class Functor:
  pass

class Controlled(Functor):

  #TODO: Add type annotation for operation.
  #TODO: Refine return type with structured typing if possible.
  def __class_getitem__(cls, operation) -> Callable:
    if not getattr(operation, '__isqdef__', False):
      raise RuntimeError(f'{operation} is not a quantum operation')
    return operation.__ctl__

class Adjoint(Functor):

  #TODO: Add type annotation for operation.
  #TODO: Refine return type with structured typing if possible.
  def __class_getitem__(cls, operation) -> Callable:
    if not getattr(operation, '__isqdef__', False):
      raise RuntimeError(f'{operation} is not a quantum operation')
    return operation.__adj__

from qiskit.extensions.standard.x import XGate

@qdef
def X(q: QData):
  q.allocation.circuit.x(q.qiskit_qubits)

@qdef
def _X_ctl(control: Union[AllOneControl, QData], q: QData):
  #TODO: Provide a decorator for adding the proper runtime signature checks.
  _multiplexed_control(XGate, control, q)

setattr(X, '__adj__', X)
setattr(X, '__ctl__', _X_ctl)
setattr(_X_ctl, '__adj__', _X_ctl)
setattr(_X_ctl, '__ctl__', _X_ctl)

from qiskit.extensions.standard.h import HGate

@qdef
def H(q: QData):
    q.allocation.circuit.h(q.qiskit_qubits)

@qdef
def _H_ctl(control: Union[AllOneControl, QData], q: QData):
  #TODO: Provide a decorator for adding the proper runtime signature checks.
  _multiplexed_control(HGate, control, q)

setattr(H, '__adj__', H)
setattr(H, '__ctl__', _H_ctl)
setattr(_H_ctl, '__adj__', _H_ctl)
setattr(_H_ctl, '__ctl__', _H_ctl)

def R1(angle: float, q: QData):
  pass

def Z(q: QData):
  pass

from qiskit.extensions.standard.iden import IdGate
from qiskit.extensions.quantum_initializer.ucg import UCG

def _multiplexed_control(gate_class, control: Union[AllOneControl, QData], target: QData):
  # TODO: Now not considering the order because this is being controlled by
  # the all 1s sequence.
  if isinstance(control, QData):
    control = AllOneControl(control)

  control_qubits = tuple(chain(
    *(value.qiskit_qubits for value in control.values)))
  control_patterns_count = 2 ** len(control_qubits)
  gate_list = [
    IdGate().to_matrix()
    for _ in range(control_patterns_count - 1)] + [gate_class().to_matrix()]
  target.allocation.circuit.append(
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

  qubits: Tuple[QData, ...]

  def __init__(self, *sizes: int):
    registers = bp.new_registers(*sizes)
    circuit = bp.new_circuit_with_registers(registers)
    self.circuit = circuit
    self.qubits = tuple(map(partial(QData, self), registers))

  def __enter__(self):
    return self

  def __exit__(self, *_):
    pass

  def __iter__(self) -> Iterable[QData]:
    return iter(self.qubits)

def allocate(*sizes: int) -> Allocation:
  return Allocation(*sizes)


_MEASUREMENT_PROXY_CACHE: MutableMapping[QData, MeasurementProxy] = {}

def measure(register: QData, reset=False) -> MeasurementProxy:
  if not register in _MEASUREMENT_PROXY_CACHE:
    circuit = register.allocation.circuit
    cregister = bp.ClassicalRegister(len(register))
    qregister = register.qiskit_qubits
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

