from typing import Type, TypeVar, Generic, Iterable, List, Callable

T = TypeVar('T')
P = TypeVar('P')

class Qubit:

  def __iter__(self):
    pass


class MetaFunctor(type):

  def __getitem__(self, index: Type[T]) -> T:
    pass

  def __add__(self, another: MetaFunctor) -> MetaFunctor:
    pass

class Functor:
  def __class_getitem__(cls, params):
    pass

class Controlled(Functor, meta=MetaFunctor):

  def __enter__(self):
    pass

  def __exit__(self, *_):
    pass

  def __call__(self, *args, **kwargs):
    pass

Ctl = Controlled

class Adjoint(Functor, meta=MetaFunctor):

  def __enter__(self):
    pass

  def __exit__(self, *_):
    pass

  def __call__(self, *args, **kwargs):
    pass

Adj = Adjoint

def X(q: Qubit):
  pass

def H(q: Qubit):
  pass

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

  def __enter__(self):
    pass

  def __exit__(self, *_):
    pass

  def __iter__(self) -> Iterable[List[Qubit]]:
    pass

def allocate(*sizes: int) -> Allocation:
  return Allocation()


class Measurement:

  def __bool__(self):
    pass

  def __int__(self):
    pass


def measure(register: Qubit, reset=False) -> Measurement:
  return Measurement()


class SafeContext:

  def __init__(self, a: Allocation):
    pass

  def __enter__(self):
    pass

  def __exit__(self, *_):
    pass

  def __iter__(self):
    pass

def reset(a: Allocation) -> SafeContext:
  return SafeContext(a)