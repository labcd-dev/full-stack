from numpy import *

def dynamics(t, x, u):
    A, q1, q2, Wa10, Wb10 = 1.0, 0.5, 0.5, 3e-3, 3e-4
    h1, h2, Wa2 = x[0], x[1], x[2]
    Wb2 = u * Wb10
    xdot = array([[(q1 - q2)/A],
            [(q2 - 0.1*sqrt(h2))/A],
            [(Wa10*q1 - Wa2*q2 - Wb2 + u*Wb10)/h2]])
    return xdot