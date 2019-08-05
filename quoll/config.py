import qiskit
import quoll.boilerplate as bp

qiskit.IBMQ.load_account()

_PROVIDERS = { 'basicaer': qiskit.BasicAer, 'ibmq': qiskit.IBMQ.get_provider() }

_BACKEND = qiskit.BasicAer.get_backend('qasm_simulator')

def get_backend():
  return _BACKEND

def set_backend(backend):
  _BACKEND = backend

def resolve_backend(provider_name, backend_name):
  if provider_name not in _PROVIDERS:
    raise ValueError(f'No provider with id {provider_name}')

  provider = _PROVIDERS[provider_name]
  return provider.get_backend(backend_name)