"""
Provide command line interface. Basic usage, considering a Qiskit account:

  quoll -b ibmq:ibmqx4 samples.bell:main

"""
import sys
from argparse import ArgumentParser
from importlib import import_module

import quoll.config
import quoll.activate

def build_parser():
  parser = ArgumentParser()
  parser.add_argument('modulefunc', type=str, help='function path in the format \'package.module:function_name\'')
  parser.add_argument('-b', '--backend', type=str, help='backend name the format \'provider:backend_name\'')
  parser.add_argument('--show-python', type=str, help='prints the Python transpiled source, use \'-\' to print in the stdout')
  return parser

def main():
  parser = build_parser()
  args = parser.parse_args()
  if args.show_python is not None:
    quoll.config.set_show_python(True, filepath=args.show_python)

  if args.backend:
    provider, backend_name = args.backend.split(':')
    backend = quoll.config.resolve_backend(provider, backend_name)
    quoll.config.set_backend(backend)

  module_name, function_name = args.modulefunc.split(':')
  module = import_module(module_name)
  function = getattr(module, function_name)
  function()

if __name__ == '__main__':
  main()