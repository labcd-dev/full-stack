import numpy as np

def dynamics(t, x, u):
    mp, mw, lp, Ip, Iw = 1, 0.5, 0.5, 0.1, 0.01
    bp, bw, g = 0.01, 0.05, 9.81
    
    theta, dtheta, phi, dphi = x[0], x[1], x[2], x[3]
    
    # Equations of motion with momentum exchange
    M = Ip + Iw + mp*lp**2
    tau_p = -mp*g*lp*np.sin(theta) - bp*dtheta + u
    tau_w = -u - bw*dphi
    
    ddtheta = (tau_p - tau_w) / M
    ddphi = tau_w / Iw - ddtheta
    
    xdot = [dtheta, ddtheta, dphi, ddphi]
    return np.array(xdot)