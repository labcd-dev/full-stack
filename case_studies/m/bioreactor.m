function xdot = dynamics(t, x, u)
    mumax = 0.5; Ks = 0.5; Yxs = 0.5; Yps = 0.2; D = 0.1;
    Sin = 10;
    X = x(1); S = x(2); P = x(3);
    mu = mumax * S / (Ks + S);
    xdot = [mu*X - D*X + u;
            -mu*X/Yxs + D*(Sin - S);
            mu*X*Yps - D*P];
end