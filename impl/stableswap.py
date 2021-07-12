from scipy.optimize import fsolve
from scipy.stats import gmean

# Pure invariant-based exchange--no LP fees, no admin fees, no repegging.
class StableSwap:

    def __init__(self, tokens, A):
        self.tokens = tokens
        N = self.N = len(tokens)
        self.balances = [0] * N
        self.A = A
        self.D = 0.0
        self.supply = 0

    def add_liquidity(self, amounts):
        N = self.N
        assert(len(amounts) == N)

        for i in range(N):
            self.balances[i] += amounts[i]

        old_D = self.D
        new_D = self.calc_D(self.A, self.balances)

        # Not assessing admin fee for now
        d_token = 0
        if old_D > 0:
            d_token = self.supply * (new_D / old_D - 1)
        else:
            d_token = new_D

        self.D = new_D
        self.supply += d_token

        # return # of LP shares minted
        return d_token

    def exchange(self, i, j, dx):
        N = self.N
        assert(i != j)
        assert(i < N)
        assert(j < N)
        assert(dx > 0)

        dy = self.calc_exchange(i, j, dx)
        assert(dy > 0)
        self.balances[i] += dx
        self.balances[j] -= dy
        return dy

    # side-effect free function for analysis
    def calc_exchange(self, i, j, dx):
        N = self.N
        xp = self.balances.copy()
        xp[i] += dx
        yp = self.calc_y(self.A, xp, self.D, j)
        return xp[j] - yp

    def calc_D(self, A, xp):
        N    = len(xp)
        NN   = N**N
        summ = sum(xp)
        prod = 1.
        for i in range(N):
            prod *= xp[i]
        def f(D):
            DN = D**N
            K0 = prod * NN / DN
            K = A * K0
            return K*(DN * summ / D - DN) + prod - DN / NN
        D0 = N * gmean(xp)
        return fsolve(f, [D0])[0]

    def calc_y(self, A, xp, D, j):
        N = len(xp)
        assert(j < N)
        NN = N**N
        DN = D**N
        summ_ = 0.
        prod_ = 1.
        for i in range(N):
            if i == j:
                continue
            summ_ += xp[i]
            prod_ *= xp[i]
        def f(y):
            summ = y + summ_
            prod = y * prod_
            K0 = prod * NN / DN
            K = A * K0
            return K*(DN * summ / D - DN) + prod - DN / NN
        y0 = DN / (prod_ * NN)
        return fsolve(f, [y0])[0]
    
    def get_virtual_price(self):
        D = self.calc_D(self.A, self.balances)
        return D / self.supply
