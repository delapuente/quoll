from abc import ABC, abstractmethod, abstractproperty
from typing import Type, TypeVar, Generic, Iterable, List, Callable, Tuple, Sequence, MutableMapping
from functools import partial

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
class QData:

  allocation: 'Allocation'

  register: bp.QuantumRegister

  def __init__(self, allocation: 'Allocation', register: bp.QuantumRegister):
    self.allocation = allocation
    self.register = register

  def __iter__(self):
    return iter(self.register)

  def __len__(self):
    return len(self.register)


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
  q.allocation.circuit.x(q.register)

@qdef
def _X_ctl(control: List[QData], q: QData):
  #TODO: Provide a decorator for adding the proper runtime signature checks.
  _multiplexed_control(XGate, control, q)

setattr(X, '__adj__', X)
setattr(X, '__ctl__', _X_ctl)
setattr(_X_ctl, '__adj__', _X_ctl)
setattr(_X_ctl, '__ctl__', _X_ctl)

from qiskit.extensions.standard.h import HGate

@qdef
def H(q: QData):
    q.allocation.circuit.h(q.register)

@qdef
def _H_ctl(control: List[QData], q: QData):
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

def _multiplexed_control(gate_class, control: List[QData], target: QData):
  # TODO: Now not considering the order because this is being controlled by
  # the all 1s sequence.
  control_registers = list(map(lambda qdata: qdata.register, control))
  control_patterns_count = 2 ** sum(reg.size for reg in control_registers)
  gate_list = [
    IdGate().to_matrix()
    for _ in range(control_patterns_count - 1)] + [gate_class().to_matrix()]
  target.allocation.circuit.append(
    UCG(gate_list, False), [target.register] + control_registers)

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

