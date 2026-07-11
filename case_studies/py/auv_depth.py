import numpy as np

def dynamics(t, x, u):
    m, Iz, W, B, zb, zg = 50, 5, 500, 510, -0.1, 0
    Zw, Zq, Zd, Mw, Mq, Md = -20, -5, -10, -3, -8, -5
    z, w, theta, q = x[0], x[1], x[2], x[3]
    xdot = [w*np.cos(theta) - np.sin(theta),
            (Zw*w + Zq*q + Zd*u + (W-B)*np.sin(theta)) / m,
            q,
            (Mw*w + Mq*q + Md*u + (zg*W - zb*B)*np.sin(theta)) / Iz]
    return np.array(xdot)