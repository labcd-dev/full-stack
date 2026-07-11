from numpy import *

def quadcopter_equations_of_motion(t, state, U):
    """
    Computes the state derivatives for a 6-DOF quadcopter.

    State vector:
    state = [x, y, z, dx, dy, dz, phi, theta, psi, p, q, r]
    Where:
        x, y, z      : Position in world frame (z is up)
        dx, dy, dz   : Velocity in world frame
        phi, theta, psi : Euler angles (Roll, Pitch, Yaw)
        p, q, r      : Angular velocities in body frame

    Control Inputs (U):
    U = [U1, U2, U3, U4]
    Where:
        U1 : Total thrust (N)
        U2 : Roll moment (N*m)
        U3 : Pitch moment (N*m)
        U4 : Yaw moment (N*m)
    """
    # --- Physical Constants & Quadcopter Parameters ---
    g = 9.81  # Acceleration due to gravity (m/s^2)
    m = 1.0  # Mass of the quadcopter (kg)

    # Moment of inertia matrix components (kg*m^2)
    Ixx = 0.005
    Iyy = 0.005
    Izz = 0.009

    # Unpack state
    x, y, z, dx, dy, dz, phi, theta, psi, p, q, r = state
    U1, U2, U3, U4 = U

    # Pre-compute trig functions for readability
    s_phi, c_phi = sin(phi), cos(phi)
    s_the, c_the = sin(theta), cos(theta)
    s_psi, c_psi = sin(psi), cos(psi)

    # 1. Translational Accelerations (World Frame)
    # Mapping total thrust U1 from body frame to world frame using Rotation Matrix (Z-Y-X convention)
    ddx = (1 / m) * (c_psi * s_the * c_phi + s_psi * s_phi) * U1
    ddy = (1 / m) * (s_psi * s_the * c_phi - c_psi * s_phi) * U1
    ddz = (1 / m) * (c_the * c_phi) * U1 - g

    # 2. Rotational Accelerations (Body Frame Angular Velocities)
    # Euler's equations for rigid body dynamics
    dp = (U2 + (Iyy - Izz) * q * r) / Ixx
    dq = (U3 + (Izz - Ixx) * p * r) / Iyy
    dr = (U4 + (Ixx - Iyy) * p * q) / Izz

    # 3. Kinematic Kinematics (Mapping body angular rates p,q,r to Euler angle rates dphi, dtheta, dpsi)
    # Note: Singularity exists at theta = +-90 degrees (gimbal lock)
    dphi = p + q * s_phi * tan(theta) + r * c_phi * tan(theta)
    dtheta = q * c_phi - r * s_phi
    dpsi = q * s_phi / c_the + r * c_phi / c_the

    # Return derivatives matching the state vector order
    return [dx, dy, dz, ddx, ddy, ddz, dphi, dtheta, dpsi, dp, dq, dr]
