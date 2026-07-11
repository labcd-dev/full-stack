import numpy as np

def dynamics(t, x, u):
    m1, m2, l1, l2, lc1, lc2 = 1, 1, 1, 1, 0.5, 0.5
    I1, I2, g = 0.1, 0.1, 9.81
    q1, dq1, q2, dq2 = x[0], x[1], x[2], x[3]
    
    # Mass matrix
    M11 = m1*lc1**2 + m2*(l1**2 + lc2**2 + 2*l1*lc2*np.cos(q2)) + I1 + I2
    M12 = m2*(lc2**2 + l1*lc2*np.cos(q2)) + I2
    M22 = m2*lc2**2 + I2
    
    # Coriolis and gravity terms
    h = -m2*l1*lc2*np.sin(q2)
    C1 = h*dq2**2 + 2*h*dq1*dq2
    C2 = -h*dq1**2
    G1 = (m1*lc1 + m2*l1)*g*np.sin(q1) + m2*lc2*g*np.sin(q1+q2)
    G2 = m2*lc2*g*np.sin(q1+q2)
    
    # Solve for accelerations
    detM = M11*M22 - M12**2
    ddq1 = (M22*(u - C1 - G1) - M12*(-C2 - G2)) / detM
    ddq2 = (M11*(-C2 - G2) - M12*(u - C1 - G1)) / detM
    
    xdot = [dq1, ddq1, dq2, ddq2]
    return np.array(xdot)