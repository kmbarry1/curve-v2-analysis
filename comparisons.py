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
  yp = p.calc_y(p.A, p.gamma, xp, p.D, 1)
  return yp / p.price_scale[1]

def y_stableswap(x):
  xp = p.balances.copy()
  xp[0] = x
  xp = p.calc_scaled_bals(xp)
  yp = p.calc_y_stableswap(p.A, xp, p.D, 1)
  return yp / p.price_scale[1]

def reserves(show_ss=False):
  x = []
  y = []
  y_uni = []
  y_ss  = []
  b = p.balances
  k = b[0] * b[1]
  for dx in dxs:
    new_x = b[0] + dx
    x.append(new_x)
    y.append(y_curveswap(new_x))
    y_uni.append(k / new_x)
    y_ss.append(y_stableswap(new_x))

  if show_ss:
    plt.plot(x, y, 'r', x, y_uni, 'b', x, y_ss, 'g')
  else:
    plt.plot(x, y, 'r', x, y_uni, 'b')

def price(show_ss=False):
  x = []
  price = []
  price_uni = []
  price_ss  = []
  b = p.balances
  k = b[0] * b[1]
  for dx in dxs:
    new_x = b[0] + dx
    x.append(new_x)
    price.append(-1. * derivative(y_curveswap, new_x))
    price_uni.append(k / new_x**2)
    price_ss.append(-1. * derivative(y_stableswap, new_x))

  plt.plot(x, price_uni, 'b', label="xy = k")
  if show_ss:
    plt.plot(x, price_ss, 'g', label="StableSwap")
  plt.plot(x, price, 'r', label="CurveSwap")

  plt.xlabel("Token 0 Reserves", fontsize=16)
  plt.ylabel("Token 0 Price", fontsize=16)
  plt.legend(loc='upper right')
  plt.title("$A={}$    $\gamma={:.5f}$".format(A, gamma), fontsize=20)

def gamma_price():
  x = []
  price = []
  price_g1 = []
  price_g2  = []
  b = p.balances
  k = b[0] * b[1]
  for dx in dxs:
    new_x = b[0] + dx
    x.append(new_x)
    price.append(-1. * derivative(y_curveswap, new_x))
    p.gamma = 10 * p.gamma
    price_g1.append(-1. * derivative(y_curveswap, new_x))
    p.gamma = 10 * p.gamma
    price_g2.append(-1. * derivative(y_curveswap, new_x))
    p.gamma = gamma

  plt.plot(x, price, 'r', x, price_g1, 'b', x, price_g2, 'g')

def A_price():
  x = []
  price = []
  price_g1 = []
  price_g2  = []
  b = p.balances
  k = b[0] * b[1]
  for dx in dxs:
    new_x = b[0] + dx
    x.append(new_x)
    price.append(-1. * derivative(y_curveswap, new_x))
    p.A = 10 * p.A
    price_g1.append(-1. * derivative(y_curveswap, new_x))
    p.A = A

  plt.plot(x, price, 'r', x, price_g1, 'b')
