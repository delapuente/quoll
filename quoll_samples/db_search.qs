namespace Microsoft.Quantum.Samples.DatabaseSearch {
  open Microsoft.Quantum.Intrinsic;
  open Microsoft.Quantum.Convert;
  open Microsoft.Quantum.Math;
  open Microsoft.Quantum.Canon;
  open Microsoft.Quantum.Arrays;
  open Microsoft.Quantum.Measurement;
  open Microsoft.Quantum.Diagnostics;
  open Microsoft.Quantum.Oracles;
  open Microsoft.Quantum.AmplitudeAmplification;

"--------"
  operation ApplyDatabaseOracle(markedQubit : Qubit, databaseRegister : Qubit[]) : Unit is Adj + Ctl {
    Controlled X(databaseRegister, markedQubit);
  }

  operation ApplyUniformSuperpositionOracle(databaseRegister : Qubit[]) : Unit is Adj + Ctl {
    ApplyToEachCA(H, databaseRegister);
  }

  operation ApplyStatePreparationOracle (markedQubit : Qubit, databaseRegister : Qubit[]) : Unit is Adj + Ctl {
    ApplyUniformSuperpositionOracle(databaseRegister);
    ApplyDatabaseOracle(markedQubit, databaseRegister);
  }

  operation ReflectAboutMarkedState(markedQubit : Qubit) : Unit {
    R1(PI(), markedQubit);
  }

  operation ReflectAboutZero(databaseRegister : Qubit[]) : Unit {
    within {
      ApplyToEachCA(X, databaseRegister);
    } apply {
      Controlled Z(Rest(databaseRegister), Head(databaseRegister));
    }
  }

  operation ReflectAboutInitialState(markedQubit : Qubit, databaseRegister : Qubit[]) : Unit {
    within {
      Adjoint ApplyStatePreparationOracle(markedQubit, databaseRegister);
    } apply {
      ReflectAboutZero([markedQubit] + databaseRegister);
    }
  }

  operation SearchForMarkedState(nIterations : Int, markedQubit : Qubit, databaseRegister : Qubit[]) : Unit {
    ApplyStatePreparationOracle(markedQubit, databaseRegister);
    for (idx in 0 .. nIterations - 1) {
      ReflectAboutMarkedState(markedQubit);
      ReflectAboutInitialState(markedQubit, databaseRegister);
    }
  }

  operation ApplyQuantumSearch (nIterations : Int, nDatabaseQubits : Int) : (Result, Result[]) {
    using ((markedQubit, databaseRegister) = (Qubit(), Qubit[nDatabaseQubits])) {
      SearchForMarkedState(nIterations, markedQubit, databaseRegister);
      let resultSuccess = MResetZ(markedQubit);
      let resultElement = ForEach(MResetZ, databaseRegister);
      return (resultSuccess, resultElement);
    }
  }

"--------"
  operation StatePreparationOracleTest() : Unit {
    for (nDatabaseQubits in 0 .. 5) {
      using ((markedQubit, databaseRegister) = (Qubit(), Qubit[nDatabaseQubits])) {
        ApplyStatePreparationOracle(markedQubit, databaseRegister);
        let successAmplitude = 1.0 / Sqrt(IntAsDouble(2 ^ nDatabaseQubits));
        let successProbability = successAmplitude * successAmplitude;
        AssertProb(
          [PauliZ], [markedQubit], One,
          successProbability,
          "Error: Success probability does not match theory", 1E-10
        );
        Reset(markedQubit);
        ResetAll(databaseRegister);
      }
    }
  }

"--------"
  operation GroverHardCodedTest () : Unit {
    for (nDatabaseQubits in 0 .. 4) {
      for (nIterations in 0 .. 5) {
        using ((markedQubit, databaseRegister) = (Qubit(), Qubit[nDatabaseQubits])) {
          SearchForMarkedState(nIterations, markedQubit, databaseRegister);
          let dimension = IntAsDouble(2 ^ nDatabaseQubits);
          let successAmplitude = Sin(
            IntAsDouble(2 * nIterations + 1) *
            ArcSin(1.0 / Sqrt(dimension))
          );
          let successProbability = PowD(successAmplitude, 2.0);
          AssertProb(
            [PauliZ], [markedQubit], One,
            successProbability,
            "Error: Success probability does not match theory", 1E-10
          );
          let isMarked = MResetZ(markedQubit) == One;
          if (isMarked) {
            let results = ForEach(MResetZ, databaseRegister);
            for (result in results) {
              EqualityFactR(result, One, "Found state should be 1..1 string.");
            }
          }
        }
      }
    }
  }
}