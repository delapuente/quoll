from dataclasses import dataclass

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.result import Result

@dataclass
class MeasurementProxy:

  circuit: QuantumCircuit

  quantum_register: QuantumRegister

  classical_register: ClassicalRegister

@dataclass
class Measurement:

  proxy: MeasurementProxy

  result: Result