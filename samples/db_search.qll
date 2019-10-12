# Transcription of:
# https://github.com/microsoft/Quantum/blob/master/samples/algorithms/database-search/DatabaseSearch.qs

from quoll.preamble import *
from quoll.assertions import *
from math import pi, sin, asin, sqrt

"--------"
@qdef(adj=True, ctl=True)
def ApplyDatabaseOracle(markedQubit, dbRegister):
  Controlled[X](dbRegister, markedQubit)

@qdef(adj=True, ctl=True)
def ApplyUniformSuperpositionOracle(dbRegister):
  map(H, dbRegister)

@qdef(adj=True, ctl=True)
def ApplyStatePreparationOracle(markedQubit, dbRegister):
  ApplyUniformSuperpositionOracle(dbRegister)
  ApplyDatabaseOracle(markedQubit, dbRegister)

@qdef
def ReflectAboutMarkedState(markedQubit):
  R1(pi, markedQubit)

@qdef
def ReflectAboutZero(dbRegister):
  map(X, dbRegister)
  Controlled[Z](dbRegister[1:], dbRegister[0])
  map(X, dbRegister)

@qdef
def ReflectAboutInitialState(markedQubit, dbRegister):
  Adjoint[ApplyStatePreparationOracle](markedQubit, dbRegister)
  ReflectAboutZero(markedQubit + dbRegister)
  ApplyStatePreparationOracle(markedQubit, dbRegister)

def SearchForMarkedState(nIterations, markedQubit, dbRegister):
  ApplyStatePreparationOracle(markedQubit, dbRegister)
  for idx in range(nIterations):
    ReflectAboutMarkedState(markedQubit)
    ReflectAboutInitialState(markedQubit, dbRegister)

def ApplyQuantumSearch(nIterations, nDatabaseQubits):
  with allocation(1, nDatabaseQubits) as (markedQubit, dbRegister):
    SearchForMarkedState(nIterations, markedQubit, dbRegister)
    resultSuccess = measure(markedQubit)
    resultElement = measure(dbRegister)
    return bool(resultSuccess), int(resultElement)

"--------"
def StatePreparationOracleTest():
  for nDatabaseQubits in range(1, 6):
    with allocation(1, nDatabaseQubits) as (markedQubit, dbRegister):
      ApplyStatePreparationOracle(markedQubit, dbRegister)
      successAmplitude = 1.0 / sqrt(2 ** nDatabaseQubits)
      successProbability = successAmplitude**2
      assertProb(
        [measure(markedQubit)], [1],
        prob=successProbability, delta=1E-1,
        msg='Error: Success probability does not match theory'
      )

"--------"
def GroverHardCodedTest():
  for nDatabaseQubits in range(1, 5):
    for nIterations in range(6):
      with allocation(1, nDatabaseQubits) as (markedQubit, dbRegister):
        SearchForMarkedState(nIterations, markedQubit, dbRegister)
        dimension = 2.0 ** nDatabaseQubits
        successAmplitude = sin(
          (2.0 * nIterations + 1.0) *
          asin(1.0 / sqrt(dimension))
        )
        successProbability = successAmplitude ** 2.0
        assertProb(
          [measure(markedQubit)], [1],
          prob=successProbability, delta=1E-1,
          msg='Error: Success probability does not match theory'
        )
        if measure(markedQubit):
          result = measure(dbRegister)
          assertFact(
            result == dbRegister.all_ones_value(),
            'Found state should be 1..1 string.')

def main():
  StatePreparationOracleTest()
  GroverHardCodedTest()
  print('Everything is fine!')