from numpy import *
from scipy.optimize import fsolve
from scipy.integrate import solve_ivp
from scipy.integrate import quad
from scipy.integrate import solve_bvp

# Case 1: Polynomial Roots
r = roots(array([1, -5, 6]))

# Case 2: Single-Variable Root Finding with Anonymous Function
val = fsolve(lambda x: x**2 - 4, 1)[0]

# Case 3: Single-Variable Root Finding with Named Function Handles
result = fsolve(my_func, array([0, 5]))[0]

# Case 4: Non-linear System of Equations - Vectorized Notation
sol = fsolve(lambda x: array([x[0] + x[1] - 3, x[0]**2 + x[1]**2 - 9]), array([1, 2]))

# Case 5: Passing Extra Parameters to Equation Solvers
res = fsolve(target_func, 0.5, args=(p1, p2))[0]

# Case 6: Standard Initial Value Problem with Anonymous Function
sol = solve_ivp(lambda t, y: 2*t, array([0, 10]), array([1]), method='RK45')
t, y = sol.t, sol.y[0]

# Case 7: Systems of ODEs (Vectorized State)
sol = solve_ivp(lambda t, y: array([y[1], -y[0]]), array([0, 5]), array([1, 0]), method='RK45')
t, y = sol.t, sol.y.T

# Case 8: ODE with Function Handle and Extra Arguments
sol = solve_ivp(my_drives, tspan, y0, args=(alpha,), method='RK45')
t, y = sol.t, sol.y.T

# Case 9: Stiff ODE Solver
sol = solve_ivp(lambda t, y: -1000*y, array([0, 1]), array([1]), method='Radau')
t, y = sol.t, sol.y[0]

# Case 10: Numerical Quadrature / Integration
q, _ = quad(lambda x: exp(-x**2), 0, inf)

# Case 11: Boundary Value Problems
sol = solve_bvp(bvp_ode, bvp_bc, solinit.x, solinit.y)
