import numpy as np

def dynamics(t, x, u):
    """
    Computes the derivatives for the bioreactor system.

    Args:
        t (float): Current time.
        x (array_like): State vector [X, S, P].
        u (array_like or float): Control input.

    Returns:
        np.ndarray: The time derivatives of the states.
    """
    mumax = 0.5
    Ks = 0.5
    Yxs = 0.5
    Yps = 0.2
    D = 0.1
    Sin = 10.0

    X, S, P = x[0], x[1], x[2]
    # Ensure u is a scalar if passed as an array
    u_val = np.atleast_1d(u)[0]

    mu = mumax * S / (Ks + S)
    xdot = [mu*X - D*X + u_val,
            -mu*X/Yxs + D*(Sin - S),
            mu*X*Yps - D*P]
    return np.array(xdot, dtype=float)