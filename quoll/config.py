import os
from configparser import ConfigParser

import qiskit
import quoll.boilerplate as bp
from quoll.unparser import unparse

_PROVIDERS = { 'basicaer': qiskit.BasicAer }
if hasattr(qiskit, 'IBMQ'):
  qiskit.IBMQ.load_account()
  _PROVIDERS['ibmq'] = qiskit.IBMQ.get_provider()

if hasattr(qiskit, 'Aer'):
  _PROVIDERS['aer'] = qiskit.Aer

_CONFIG_FILE = 'quoll.ini'

_BACKEND = 'basicaer:qasm_simulator'

_SHOW_PYTHON = False

def get_config_file():
  return _CONFIG_FILE

def set_config_file(config_file):
  global _CONFIG_FILE
  _CONFIG_FILE = config_file

def get_backend():
  return _resolve_backend(*_BACKEND.split(':'))

def set_backend(backend):
  global _BACKEND
  _BACKEND = backend

def _resolve_backend(provider_name, backend_name):
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

def get_shots():
  fallback = 1024
  config = ConfigParser()
  config.read(get_config_file())
  section = _get_backend_matching_section(_BACKEND, config)
  return config[section].getint(
    'shots', fallback=fallback) if section else fallback

def _get_backend_matching_section(backend_id, config):
  sections = config.keys()
  for one_section in sections:
    if one_section.startswith('backend:'):
      _, config_backend_id = one_section.split(':', 1)
      if config_backend_id == '*' or config_backend_id == backend_id:
        return one_section