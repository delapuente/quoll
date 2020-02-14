# Quoll
> The other animal starting with Q.

Quoll is a Python library that extends the language to add quantum-circuit-oriented, high-level features. Like this:

```python
from quoll.preamble import *
from quoll.assertions import *

with allocation(1, 1) as (control, target):
  H(control)
  if superposition(control == 1):
    X(target)

  assertProb([measure(control), measure(target)], [1, 1], 0.5)
  print('Everything working as expected.')
```

Quoll is based on [Qiskit Terra](https://github.com/qiskit/qiskit-terra) for creating the circuits and can use IBM real devices and simulators to execute the circuits.

## Install
Right now,  Quoll is completely experimental and lives only in GitHub. If you want to give it a try, install from the repository:

```bash
$ pip install git+https://github.com/delapuente/quoll.git
```

This install the packages `quoll` and `quoll_samples` where you can find a [variety of examples and algorithms](https://github.com/delapuente/quoll/tree/master/samples) implemented in Quoll.

## Usage

Quoll integrates with IPython, so you can start by launching an IPython session or by creating a new **Jupyter notebook**, then doing:

```python
import quoll.activate
```

Make sure you **run** the previous line before start using Quoll syntax.

```python
from quoll.preamble import *
from quoll.assertions import *

with allocation(1, 1) as (control, target):
  H(control)
  if superposition(control == 1):
    X(target)

  assertProb([measure(control), measure(target)], [1, 1], 0.5)
  print('Everything working as expected.')
```

### Working with files
Regularly, Quoll [works](#how-does-it-work) at import time, which means you need to run a regular Python file, activate Quoll and start importing `.qll` files containing the extended syntax. For instance:

```python
# in bell_test.qll
from quoll.preamble import *
from quoll.assertions import *

@qdef(adj=True)
def bell(c, t):
  H(c)
  Controlled[X](c, t)

def test_bell_adjoint():
  with allocation(1, 1) as (control, target):
    bell(c, t)
    Adjoint[bell](c, t)
    assertProb([measure(c+t)], [0], 1.0)
    print('Quantum mechanics are working!')
```

```python
# in main.py
import quoll.activate
from bell_test import test_bell_adjoint

if __name__ == '__python__':
  test_bell_adjoint()
```

So now you can just run the Python file:

```bash
$ python main.py
```

### The CLI

With the Quoll CLI, you can run Quoll code directly by specifying the module and entry point as follows:

```bash
$ quoll bell_test:test_bell_adjoint
```

## How does it work?

Quoll works by hooking into Python import mechanism and adding a new loader for `*.qll` files. When a Quoll file is found, its abstract tree is statically analaysed and transformed into an equivalent Python program depending on Quoll libraries which are pure Python.

IPython support works [thanks to some hooks in the environment](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html#ast-transformations).

### Inspecting the generated Python code

If you want to inspect the generated Python code for the `*.qll` files, remove the `__pycache__` folders or the `*.pyc` files for the module you want to see expanded and use the CLI passing the `--show-python` option.

```bash
$ PYTHONDONTWRITEBYTECODE=1 quoll --show-python bell_test:test_bell_adjoint
```

Setting `PYTHONDONTWRITEBYTECODE` is useful to avoid writing Python bytecode.


