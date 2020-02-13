import quoll.preamble
import quoll.boilerplate as bp

class AllocationInspector:

  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      _instance = object.__new__(cls, *args, **kwargs)

    return _instance

  def show(self):
    print(bp.__ALLOCATIONS__[-1].circuit)

  @property
  def circuit(self):
    return bp.__ALLOCATIONS__[-1].circuit


class QDefInspector:

  def __call__(self, f, *args, **kwargs):
    sizes, params = self._gen_params(args)
    with quoll.preamble.allocation(*sizes) as qubits:
      f(*params(qubits), **kwargs)
      allocation().show()


  def _gen_params(self, args):
    sizes = [n for n in args if type(n) is int]
    int_indices = (i for i, n in enumerate(args) if type(n) is int)
    def _param_gen(qubits):
      qubits = [*qubits]
      for n in args:
        if type(n) is int:
          yield qubits.pop(0)
        else:
          yield n

    return sizes, _param_gen

def allocation():
  return AllocationInspector()


def qdef(f, *args, **kwargs):
  return QDefInspector()(f, *args, **kwargs)
