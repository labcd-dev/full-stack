function xdot = dynamics(t, x, u)
    ms = 300; mu = 60; ks = 16000; kt = 190000; bs = 1000;
    zs = x(1); vs = x(2); zu = x(3); vu = x(4);
    xdot = [vs,
            (-ks*(zs-zu) - bs*(vs-vu) + u) / ms,
            vu,
            (ks*(zs-zu) + bs*(vs-vu) - kt*zu - u) / mu];
end