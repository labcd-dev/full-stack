import numpy as np

def dynamics(t, x, u):
    Vm, Rt, Tm, Cp, Cv = 0.02, 287, 400, 1004, 717
    Wc, Tc, Jt, Kt, nt = 10, 350, 0.05, 0.2, 0.85
    pim, omega_t, megr = x[0], x[1], x[2]
    Wt = u  # turbine mass flow
    xdot = [Rt*Tm/Vm * (Wc - Wt - megr),
            1/Jt * (Cp*Tc*Wc*nt - Cp*Tm*Wt/nt - Kt*omega_t),
            -0.5*megr + 0.1*pim]
    return np.array(xdot)