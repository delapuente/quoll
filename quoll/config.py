import os
import qiskit
import quoll.boilerplate as bp
from quoll.unparser import unparse

_PROVIDERS = { 'basicaer': qiskit.BasicAer }
if hasattr(qiskit, 'IBMQ'):
  qiskit.IBMQ.load_account()
  _PROVIDERS['ibmq'] = qiskit.IBMQ.get_provider()

_BACKEND = qiskit.BasicAer.get_backend('qasm_simulator')

_SHOW_PYTHON = False

def get_backend():
  return _BACKEND

def set_backend(backend):
  global _BACKEND
  _BACKEND = backend

def resolve_backend(provider_name, backend_name):
  if provider_name not in _PROVIDERS:
    raise ValueError(f'No provider with id {provider_name}')

  provider = _PROVIDERS[provider_name]
  return provider.get_backend(backend_name)

def set_show_python(enabled):
  global _SHOW_PYTHON
  _SHOW_PYTHON = enabled

def show_python(translate_fn):
  def _decorated(source, path):
    module = translate_fn(source, path)
    if _SHOW_PYTHON:
      generated_python_path = f'{path}.py'
      _print_python(module, generated_python_path)
    return module

  return _decorated

def _print_python(module, path):
  abspath = _resolve_path(os.getcwd(), path)
  with open(abspath, 'w') as file_:
    print(unparse(module), file=file_)

def _resolve_path(current, relative):
  if os.path.isabs(relative):
    return relative

  return os.path.normpath(os.path.join(current, relative))
