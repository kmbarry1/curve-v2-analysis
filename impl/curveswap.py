from scipy.optimize import fsolve
from scipy.stats import gmean

# Pure invariant-based exchange--no LP fees, no admin fees, no repegging.
class CurveSwap_1:

    def __init__(self, tokens, initial_prices, A, gamma):
        self.tokens = tokens
        N = self.N = len(tokens)

        # First token is used for pricing, thus its price is always 1 and cannot be directly specified.
        assert(len(initial_prices) == (N - 1))
        self.price_scale = [1.0]
        self.price_scale.extend(initial_prices)

        self.balances = [0] * N
        self.scaled_balances = [0] * N

        self.A = A
        self.gamma = gamma

        self.D = 0.0
        self.supply = 0

    def add_liquidity(self, amounts):
        N = self.N
        assert(len(amounts) == N)

        for i in range(N):
            self.balances[i] += amounts[i]

        # For now, not tweaking prices, so assign scaled_balances here
        xp = self.scaled_balances = self.calc_scaled_bals(self.balances)

        old_D = self.D
        new_D = self.calc_D(self.A, self.gamma, xp)

        # Not assessing admin fee for now
        d_token = 0
        if old_D > 0:
            d_token = self.supply * (new_D / old_D - 1)
        else:
            d_token = self.calc_xcp(new_D)

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
        self.scaled_balances = self.calc_scaled_bals(self.balances)
        return dy

    # side-effect free function for analysis
    def calc_exchange(self, i, j, dx):
        N = self.N
        b = self.balances.copy()
        b[i] += dx
        xp = self.calc_scaled_bals(b)
        yp = self.calc_y(self.A, self.gamma, xp, self.D, j)
        y = yp / self.price_scale[j]
        return b[j] - y

    def calc_scaled_bals(self, balances):
        N = self.N
        scaled = [0] * N
        for i in range(N):
            scaled[i] = balances[i] * self.price_scale[i]
        return scaled

    def calc_xcp(self, D):
        N = self.N
        x = [0] * N
        p = self.price_scale
        for i in range(N):
            x[i] = D / (N * p[i])
        return gmean(x)

    def calc_D(self, A, gamma, xp):
        N    = len(xp)
        NN   = N**N
        summ = sum(xp)
        prod = 1.
        for i in range(N):
            prod *= xp[i]
        def f(D):
            DN = D**N
            K0 = prod * NN / DN
            K = A * K0 * gamma**2 / (gamma + 1 - K0)**2
            return K*(DN * summ / D - DN) + prod - DN / NN
        D0 = N * gmean(xp)
        return fsolve(f, [D0])[0]

    def calc_y(self, A, gamma, xp, D, j):
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
            K = A * K0 * gamma**2 / (gamma + 1 - K0)**2
            return K*(DN * summ / D - DN) + prod - DN / NN
        y0 = DN / (prod_ * NN)
        return fsolve(f, [y0])[0]

    def calc_y_stableswap(self, A, xp, D, j):
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
