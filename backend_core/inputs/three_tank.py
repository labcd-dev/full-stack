import numpy as np

def dynamics(t, x, u):
    # Parameters from the three-tank system description
    SA = 0.0154  # Cross-sectional area of tanks (m^2)
    Sn = 5e-5  # Cross-sectional area of pipes (m^2)
    alpha1 = 0.22;
    alpha2 = 0.28;
    alpha3 = 0.27  # Outflow coefficients
    g = 9.81  # Gravitational acceleration (m/s^2)

    h1 = x[0];
    h2 = x[1];
    h3 = x[2]
    # Inputs: u = [Q1; Q2] - inflow rates to tanks 1 and 2 (m^3/s)
    Q1 = u[0];
    Q2 = u[1]

    # Flow rates
    Q13 = alpha1 * Sn * np.sign(h1 - h3) * np.sqrt(2 * g * np.abs(h1 - h3))
    Q32 = alpha3 * Sn * np.sign(h3 - h2) * np.sqrt(2 * g * np.abs(h3 - h2))
    Q20 = alpha2 * Sn * np.sign(h2) * np.sqrt(
        2 * g * np.abs(h2))  # Outflow from tank 2 to reservoir (assumed at height 0)

    # State derivatives
    xdot = np.zeros(3)
    xdot[0] = (Q1 - Q13) / SA  # dh1/dt: tank 1
    xdot[2] = (Q13 - Q32) / SA  # dh3/dt: tank 3 (intermediate)
    xdot[1] = (Q2 + Q32 - Q20) / SA  # dh2/dt: tank 2
    return xdot