% Case 1: Polynomial Roots
r = roots([1, -5, 6]);

% Case 2: Single-Variable Root Finding with Anonymous Function
val = fzero(@(x) x^2 - 4, 1);

% Case 3: Single-Variable Root Finding with Named Function Handles
result = fzero(@my_func, [0, 5]);

% Case 4: Non-linear System of Equations - Vectorized Notation
sol = fsolve(@(x) [x(1) + x(2) - 3; x(1)^2 + x(2)^2 - 9], [1, 2]);

% Case 5: Passing Extra Parameters to Equation Solvers
res = fzero(@(x) target_func(x, p1, p2), 0.5);

% Case 6: Standard Initial Value Problem with Anonymous Function
[t, y] = ode45(@(t,y) 2*t, [0, 10], 1);

% Case 7: Systems of ODEs (Vectorized State)
[t, y] = ode45(@(t,y) [y(2); -y(1)], [0, 5], [1; 0]);

% Case 8: ODE with Function Handle and Extra Arguments
[t, y] = ode45(@(t,y) my_drives(t, y, alpha), tspan, y0);

% Case 9: Stiff ODE Solver
[t, y] = ode15s(@(t,y) -1000*y, [0, 1], 1);

% Case 10: Numerical Quadrature / Integration
q = integral(@(x) exp(-x.^2), 0, inf);

% Case 11: Boundary Value Problems
sol = bvp4c(@bvp_ode, @bvp_bc, solinit);
