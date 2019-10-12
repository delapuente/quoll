"""
Provide command line interface. Basic usage, considering a Qiskit account:

  quoll -b ibmq:ibmqx4 samples.bell:main

"""
import sys
from argparse import ArgumentParser
from importlib import import_module


def build_parser():
  parser = ArgumentParser()
  parser.add_argument('modulefunc', type=str, help='function path in the format \'package.module:function_name\'.')
  parser.add_argument('-b', '--backend', type=str, help='backend name the format \'provider:backend_name\'')
  parser.add_argument('--show-python', action='store_true', help='generates *.qll.py files with the Python transpiled version of the source.')
  return parser

def main():
  parser = build_parser()
  args = parser.parse_args()

  import quoll.config
  quoll.config.set_show_python(args.show_python)

  if args.backend:
    provider, backend_name = args.backend.split(':')
    backend = quoll.config.resolve_backend(provider, backend_name)
    quoll.config.set_backend(backend)

  module_and_function = args.modulefunc.split(':')
  if len(module_and_function) == 2:
    module_name, function_name = module_and_function
  else:
    module_name, function_name = module_and_function[0], None

  import quoll.activate
  module = import_module(module_name)
  if function_name:
    function = getattr(module, function_name)
    function()

if __name__ == '__main__':
  main()