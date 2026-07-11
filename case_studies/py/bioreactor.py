import numpy as np

def dynamics(t, x, u):
    mumax, Ks, Yxs, Yps, D, Sin = 0.5, 0.5, 0.5, 0.2, 0.1, 10
    X, S, P = x[0], x[1], x[2]
    mu = mumax * S / (Ks + S)
    xdot = [mu*X - D*X + u,
            -mu*X/Yxs + D*(Sin - S),
            mu*X*Yps - D*P]
    return np.array(xdot)