import numpy as np

def dynamics(t, x, u):
    L, C, R, Vin = 0.001, 0.0001, 10, 12
    iL, vC = x[0], x[1]
    D = np.clip(u, 0, 1)
    return np.array([(Vin - D*vC) / L, (D*iL - vC/R) / C])