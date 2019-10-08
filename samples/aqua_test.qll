from quoll.preamble import *
from .aqua.grover import Grover

@qdef(adj=True)
def db_oracle(marked_qubit, db_register):
  if control(db_register == 5):
    X(marked_qubit)

def main():
  success, found_value = Grover(db_oracle, 4).run()
  print(f'Grover finished with success={success} with found_value={found_value}')

if __name__ == '__main__':
  main()