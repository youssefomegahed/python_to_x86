def div(a, b):
    return 0 if lessthan(a, b) else div(a + -b, b) + 1


def lessthan(a, b): return True if a == 0 else False if b == 0 else lessthan(
    a + -1, b + -1)


def mult(a, b):
  return 0 if b == 0 else a + mult(a, b + -1)


def triangular_sum(f):
  return lambda n: div(prod(n, f(n + 1, n + 2)), 6)


def prod(y):
  return mult(y, y)


sum_func = triangular_sum(prod)
print sum_func(10)
