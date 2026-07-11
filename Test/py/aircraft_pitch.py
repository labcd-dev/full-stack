from numpy import *

def dynamics(t, x, u):
    m, Iy, S, c, rho, V = 1000, 3000, 16, 1.5, 1.225, 50
    CL_alpha, CM_alpha, CM_q, CM_delta = 4.5, -0.8, -15, -1.2
    theta, q, w = x[0], x[1], x[2]
    alpha = arctan(w / V)
    Q = 0.5 * rho * V**2
    L = Q * S * CL_alpha * alpha
    M = Q * S * c * (CM_alpha * alpha + CM_q * q * c / (2*V) + CM_delta * u)
    theta_dot = q
    q_dot = M/Iy
    w_dot = (L * cos(theta) - m * 9.81 * sin(theta)) / m - V * q
    xdot = array([[theta_dot], [q_dot], [w_dot]])
    return xdot