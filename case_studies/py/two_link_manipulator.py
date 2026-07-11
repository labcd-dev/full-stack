import numpy as np

def dynamics(t, x, u):
    m1, m2, l1, l2, lc1, lc2 = 1, 1, 1, 1, 0.5, 0.5
    I1, I2, g, b1, b2 = 0.083, 0.083, 9.81, 0.1, 0.1
    
    q1, q2, dq1, dq2 = x[0], x[1], x[2], x[3]
    
    # Inertia matrix
    M11 = m1*lc1**2 + m2*(l1**2 + lc2**2 + 2*l1*lc2*np.cos(q2)) + I1 + I2
    M12 = m2*(lc2**2 + l1*lc2*np.cos(q2)) + I2
    M22 = m2*lc2**2 + I2
    
    # Coriolis, centrifugal, and gravity
    h = -m2*l1*lc2*np.sin(q2)
    C = [h*dq2*(2*dq1 + dq2), -h*dq1**2]
    G = [g*(m1*lc1 + m2*l1)*np.sin(q1) + g*m2*lc2*np.sin(q1+q2),
         g*m2*lc2*np.sin(q1+q2)]
    B = [b1*dq1, b2*dq2]
    
    # Accelerations
    tau = [u, 0]  # Only first joint actuated
    detM = M11*M22 - M12**2
    ddq1 = (M22*(tau[0] - C[0] - G[0] - B[0]) - M12*(tau[1] - C[1] - G[1] - B[1])) / detM
    ddq2 = (M11*(tau[1] - C[1] - G[1] - B[1]) - M12*(tau[0] - C[0] - G[0] - B[0])) / detM
    
    xdot = [dq1, dq2, ddq1, ddq2]
    return np.array(xdot)