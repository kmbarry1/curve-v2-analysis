from impl.curveswap import CurveSwap_1
from scipy.misc import derivative
import matplotlib
import matplotlib.pyplot as plt

matplotlib.interactive(True)

A = 3645
gamma = 0.00007
p = CurveSwap_1(['A', 'B'], [2], A, gamma)
p.add_liquidity([1000, 500])

# make sure to miss 0
#dxs = range(-975, 977, 2)
#dxs = range(-501, 503, 2)
#dxs = range(-301, 303, 2)
dxs = range(-101, 103, 2)

def y_curveswap(x):
  xp = p.balances.copy()
  xp[0] = x
  xp = p.calc_scaled_bals(xp)
  yp = p.calc_y(A, gamma, xp, p.D, 1)
  return yp / p.price_scale[1]

def reserves():
  x = []
  y = []
  x_uni = []
  y_uni = []
  b = p.balances
  k = b[0] * b[1]
  for dx in dxs:
    new_x = b[0] + dx
    x.append(new_x)
    y.append(y_curveswap(new_x))
    x_uni.append(new_x)
    y_uni.append(k / new_x)

  plt.plot(x, y, 'r', x_uni, y_uni, 'b')

def price_versus_reserves():
  x = []
  price = []
  x_uni = []
  price_uni = []
  b = p.balances
  k = b[0] * b[1]

  for dx in dxs:
    new_x = b[0] + dx
    x.append(new_x)
    price.append(-1. * derivative(y_curveswap, new_x))
    x_uni.append(new_x)
    price_uni.append(k / new_x**2)

  plt.plot(x, price, 'r', x_uni, price_uni, 'b')
