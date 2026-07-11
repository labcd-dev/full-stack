function xdot = dynamics(t, x, u)
    A = 1.0; q1 = 0.5; q2 = 0.5; Wa10 = 3e-3; Wb10 = 3e-4;
    h1 = x(1); h2 = x(2); Wa2 = x(3);
    Wb2 = u * Wb10;
    xdot = [(q1 - q2)/A;
            (q2 - 0.1*sqrt(h2))/A;
            (Wa10*q1 - Wa2*q2 - Wb2 + u*Wb10)/h2];
end