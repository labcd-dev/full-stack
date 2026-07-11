import numpy as np

def dynamics(t, x, u):
    m, g, L, R, k = 0.05, 9.81, 0.01, 1.0, 0.0001
    z, v, i = x[0], x[1], x[2]
    F_mag = k * i**2 / (z**2 + 0.001)
    z_dot = v
    v_dot = g - F_mag / m
    i_dot = (u - R * i - k * i * v / (z**2 + 0.001)) / L
    return np.array([z_dot, v_dot, i_dot])