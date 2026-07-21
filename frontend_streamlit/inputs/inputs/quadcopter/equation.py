from numpy import *

def system_dynamics(t, x, u):
    # =========================================================================
    # UNIVERSAL PLANT MODEL
    # Target: Python solve_ivp / State-Space
    # =========================================================================

    ## 1. PARAMETERS (Hard-coded constants)
    # [PARAM_START]
    g = 9.81  # Acceleration due to gravity (m/s^2)
    m = 1.0   # Mass of the quadcopter (kg)
    Ixx = 0.005  # Moment of inertia matrix components (kg*m^2)
    Iyy = 0.005
    Izz = 0.009
    # [PARAM_END]

    ## 2. UNPACK STATES & INPUTS
    # [UNPACK_START]
    x, y, z, dx, dy, dz, phi, theta, psi, p, q, r = x
    U1, U2, U3, U4 = u
    # [UNPACK_END]

    ## 3. DYNAMICS / EQUATIONS OF MOTION
    # [EOM_START]
    s_phi, c_phi = sin(phi), cos(phi)
    s_the, c_the = sin(theta), cos(theta)
    s_psi, c_psi = sin(psi), cos(psi)

    ddx = (1 / m) * (c_psi * s_the * c_phi + s_psi * s_phi) * U1
    ddy = (1 / m) * (s_psi * s_the * c_phi - c_psi * s_phi) * U1
    ddz = (1 / m) * (c_the * c_phi) * U1 - g

    dp = (U2 + (Iyy - Izz) * q * r) / Ixx
    dq = (U3 + (Izz - Ixx) * p * r) / Iyy
    dr = (U4 + (Ixx - Iyy) * p * q) / Izz

    dphi = p + q * s_phi * tan(theta) + r * c_phi * tan(theta)
    dtheta = q * c_phi - r * s_phi
    dpsi = q * s_phi / c_the + r * c_phi / c_the
    # [EOM_END]

    ## 4. DERIVATIVE VECTOR CONSTRUCTION
    # [DERIVATIVE_START]
    dxdt = array([dx, dy, dz, ddx, ddy, ddz, dphi, dtheta, dpsi, dp, dq, dr])
    # [DERIVATIVE_END]

    return dxdt