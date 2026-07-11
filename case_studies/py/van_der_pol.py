import numpy as np

def dynamics(t, x, u):
    mu = 2.0
    x1, x2 = x[0], x[1]
    return np.array([x2, mu*(1 - x1**2)*x2 - x1 + u])