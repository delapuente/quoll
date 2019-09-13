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
_SHOW_PYTHON_DESTINATION = None

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

def set_show_python(enabled, filepath=''):
  global _SHOW_PYTHON, _SHOW_PYTHON_DESTINATION

  _SHOW_PYTHON = enabled
  if _SHOW_PYTHON:
    _SHOW_PYTHON_DESTINATION = filepath

def show_python(module_factory):
  def _decorated(*args, **kwargs):
    module = module_factory(*args, **kwargs)
    if _SHOW_PYTHON:
      _print_python(module, _SHOW_PYTHON_DESTINATION)
    return module

  return _decorated

def _print_python(module, path):
  if path == '-':
    print(unparse(module))
  else:
    abspath = _resolve_path(os.getcwd(), path)
    with open(abspath, 'w') as file_:
      print(unparse(module), file=file_)

def _resolve_path(current, relative):
  if os.path.isabs(relative):
    return relative

  return os.path.normpath(os.path.join(current, relative))
