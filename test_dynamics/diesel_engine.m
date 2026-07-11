function xdot = dynamics(t, x, u)
    Vm = 0.02; Rt = 287; Tm = 400; Cp = 1004; Cv = 717;
    Wc = 10; Tc = 350; Jt = 0.05; Kt = 0.2; nt = 0.85;
    pim = x(1); omega_t = x(2); megr = x(3);
    Wt = u; % turbine mass flow
    xdot = [Rt*Tm/Vm * (Wc - Wt - megr);
            1/Jt * (Cp*Tc*Wc*nt - Cp*Tm*Wt/nt - Kt*omega_t);
            -0.5*megr + 0.1*pim];
end