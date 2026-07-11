from numpy import *
import scipy.linalg as linalg

def quadcopter_dynamics(t,x,omega):
    X     = x[0]

    Y     = x[1]

    Z     = x[2]

    u     = x[3]

    v     = x[4]

    w     = x[5]

    phi   = x[6]

    theta = x[7]

    psi   = x[8]

    p     = x[9]

    q     = x[10]

    r     = x[11]

    m  = 1.5

    g  = 9.81

    Ix = 0.02

    Iy = 0.02

    Iz = 0.04

    l  = 0.25

    kf = 1.2e-5

    km = 2.4e-7

    Cd = 0.1

    w1 = omega[0]

    w2 = omega[1]

    w3 = omega[2]

    w4 = omega[3]

    F1 = kf*w1**2

    F2 = kf*w2**2

    F3 = kf*w3**2

    F4 = kf*w4**2

    T = F1 + F2 + F3 + F4

    tau_phi = l*(F2 - F4)

    tau_theta = l*(F3 - F1)

    tau_psi = km*(       w1**2     - w2**2     + w3**2     - w4**2 )

    tau = array([[tau_phi], [tau_theta], [tau_psi]])
## Rotation matrix

    cphi = cos(phi)

    sphi = sin(phi)

    cth = cos(theta)

    sth = sin(theta)

    cps = cos(psi)

    sps = sin(psi)

    R = array([[cth*cps, sphi*sth*cps-cphi*sps, cphi*sth*cps+sphi*sps], [cth*sps, sphi*sth*sps+cphi*cps, cphi*sth*sps-sphi*cps], [-sth, sphi*cth, cphi*cth]])
## Position dynamics

    vel_inertial = R*array([[u], [v], [w]])

    Xdot = vel_inertial[0]

    Ydot = vel_inertial[1]

    Zdot = vel_inertial[2]

    Vb = array([[u], [v], [w]])

    omega_b = array([[p], [q], [r]])

    Fg_body = R.conj().transpose()*array([[0], [0], [m*g]])

    Fthrust_body = array([[0], [0], [-T]])

    Fdrag = -Cd*Vb

    acc_body =      (1/m)*(Fthrust_body + Fdrag + Fg_body)      - cross(omega_b,Vb)

    udot = acc_body[0]

    vdot = acc_body[1]

    wdot = acc_body[2]
## Euler angle kinematics

    E = array([[1, sin(phi)*tan(theta), cos(phi)*tan(theta)], [0, cos(phi), -sin(phi)], [0, sin(phi)/cos(theta), cos(phi)/cos(theta)]])

    eulerdot = E*omega_b

    phidot   = eulerdot[0]

    thetadot = eulerdot[1]

    psidot   = eulerdot[2]
## Rotational dynamics

    I = diag(array([Ix, Iy, Iz]))

    omega_dot = linalg.solve(I, (tau - cross(omega_b,I*omega_b)))

    pdot = omega_dot[0]

    qdot = omega_dot[1]

    rdot = omega_dot[2]
## Assemble state derivative

    xdot = array([[Xdot], [Ydot], [Zdot], [udot], [vdot], [wdot], [phidot], [thetadot], [psidot], [pdot], [qdot], [rdot]])

    return xdot
