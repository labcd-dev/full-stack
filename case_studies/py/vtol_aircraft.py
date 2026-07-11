import numpy as np

def dynamics(t, x, u):
    m, g, Jx, Jy, Jz = 4, 9.81, 0.2, 0.3, 0.4
    x_pos, vx, phi, p, theta, q = x[0], x[1], x[2], x[3], x[4], x[5]
    T = 45  # thrust
    xdot = [vx,
            (T*np.sin(theta) - 0.1*vx) / m,
            p,
            u / Jx,
            q,
            (-T*np.sin(phi)*np.cos(theta) - 0.05*q) / Jy]
    return np.array(xdot)