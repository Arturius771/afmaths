import operation

def pythagoras(a,b):
  result = operation.square_root(operation.add(operation.exponentiate(a, 2), operation.exponentiate(b, 2)))
  print(f"Pythagoras = {result}")
  return result