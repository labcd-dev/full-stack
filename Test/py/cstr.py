from numpy import *

def dynamics(t, x, u):
    q, V, CA0, T0, Tc0 = 1, 1, 1, 350, 300
    k0, E_R, dH, rho, Cp = 7.2e10, 8750, -2e5, 1000, 0.239
    UA, rhoc, Cpc, Vc = 5e4, 1000, 1, 1
    CA, T, Tc = x[0], x[1], x[2]
    r = k0 * exp(-E_R/T) * CA
    xdot = array([[q/V*(CA0 - CA) - r],
            [q/V*(T0 - T) - dH/(rho*Cp)*r + UA/(V*rho*Cp)*(Tc - T)],
            [u/Vc*(Tc0 - Tc) + UA/(Vc*rhoc*Cpc)*(T - Tc)]])
    return xdot