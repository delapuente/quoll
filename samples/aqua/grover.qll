from quoll.preamble import *
from quoll.assertions import *
from math import pi, sin, asin, sqrt, floor

class Grover:

  def __init__(self, dbOracle, dbRegisterSize):
    self._dbOracle = dbOracle
    self._dbRegisterSize = dbRegisterSize

  def run(self):
    registerSize = self._dbRegisterSize
    iterations = floor(3/4 * pi * sqrt(2 ** registerSize))
    return self._ApplyQuantumSearch(iterations, registerSize)

  @qdef(adj=True, ctl=True)
  def _ApplyDatabaseOracle(self, markedQubit, dbRegister):
    self._dbOracle(markedQubit, dbRegister)

  @qdef(adj=True, ctl=True)
  def _ApplyUniformSuperpositionOracle(self, dbRegister):
    map(H, dbRegister)

  @qdef(adj=True, ctl=True)
  def _ApplyStatePreparationOracle(self, markedQubit, dbRegister):
    self._ApplyUniformSuperpositionOracle(dbRegister)
    self._ApplyDatabaseOracle(markedQubit, dbRegister)

  @qdef
  def _ReflectAboutMarkedState(self, markedQubit):
    R1(pi, markedQubit)

  @qdef
  def _ReflectAboutZero(self, dbRegister):
    map(X, dbRegister)
    Controlled[Z](dbRegister[1:], dbRegister[0])
    map(X, dbRegister)

  @qdef
  def _ReflectAboutInitialState(self, markedQubit, dbRegister):
    Adjoint[self._ApplyStatePreparationOracle](markedQubit, dbRegister)
    self._ReflectAboutZero(markedQubit + dbRegister)
    self._ApplyStatePreparationOracle(markedQubit, dbRegister)

  def _SearchForMarkedState(self, nIterations, markedQubit, dbRegister):
    self._ApplyStatePreparationOracle(markedQubit, dbRegister)
    for idx in range(nIterations):
      self._ReflectAboutMarkedState(markedQubit)
      self._ReflectAboutInitialState(markedQubit, dbRegister)

  def _ApplyQuantumSearch(self, nIterations, nDatabaseQubits):
    with allocation(1, nDatabaseQubits) as (markedQubit, dbRegister):
      self._SearchForMarkedState(nIterations, markedQubit, dbRegister)
      resultSuccess = measure(markedQubit)
      resultElement = measure(dbRegister)
      return bool(resultSuccess), int(resultElement)