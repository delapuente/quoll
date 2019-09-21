from quoll.preamble import *
from .aqua.grover import grover

@qdef(adj=True)
def db_oracle(marked_qubit, db_register):
  if control(db_register.is_max_value()):
    X(marked_qubit)

def main():
  success, found_value = grover(db_oracle, 3)
  print(f'Grover finished with success={success} with found_value={found_value}')

if __name__ == '__main__':
  main()