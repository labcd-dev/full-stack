import numpy as np

def dynamics(t, x, u):
    mr, mp, Lr, Lp = 0.095, 0.024, 0.085, 0.129
    Jr, Jp, Br, Bp, g = 2e-4, 4e-5, 5e-5, 1e-5, 9.81
    
    theta, alpha, dtheta, dalpha = x[0], x[1], x[2], x[3]
    
    # Mass matrix elements
    M11 = Jr + mp*Lr**2
    M12 = 0.25*mp*Lr*Lp*np.cos(alpha)
    M22 = Jp + 0.25*mp*Lp**2
    
    # Nonlinear terms
    C1 = -0.25*mp*Lr*Lp*np.sin(alpha)*dalpha**2 - Br*dtheta
    C2 = 0.125*mp*Lr*Lp*np.sin(alpha)*dtheta**2 - 0.5*mp*g*Lp*np.sin(alpha) - Bp*dalpha
    
    # Solve for accelerations
    detM = M11*M22 - M12**2
    ddtheta = (M22*(u + C1) - M12*C2) / detM
    ddalpha = (M11*C2 - M12*(u + C1)) / detM
    
    xdot = [dtheta, dalpha, ddtheta, ddalpha]
    return np.array(xdot)