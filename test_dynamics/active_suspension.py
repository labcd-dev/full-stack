import numpy as np

def dynamics(t, x, u):
    ms, mu, ks, kt, bs = 300, 60, 16000, 190000, 1000
    zs, vs, zu, vu = x[0], x[1], x[2], x[3]
    xdot = [vs,
            (-ks*(zs-zu) - bs*(vs-vu) + u) / ms,
            vu,
            (ks*(zs-zu) + bs*(vs-vu) - kt*zu - u) / mu]
    return np.array(xdot)