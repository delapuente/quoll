from setuptools import setup, find_packages

setup(
  name='quoll',
  version='0.1.0',
  description='''A quantum oriented Python dialect, enabling mixed quantum and
classical programming and saving tons of boilerplate code.''',
  entry_points={
    'console_scripts': ['quoll=quoll.cli:main']
  },
  packages=find_packages(),
  install_requires=[
    'abm',
    'qiskit'
  ]
)