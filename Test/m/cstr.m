function xdot = dynamics(t, x, u)
    q = 1; V = 1; CA0 = 1; T0 = 350; Tc0 = 300;
    k0 = 7.2e10; E_R = 8750; dH = -2e5; rho = 1000; Cp = 0.239;
    UA = 5e4; rhoc = 1000; Cpc = 1; Vc = 1;
    CA = x(1); T = x(2); Tc = x(3);
    r = k0 * exp(-E_R/T) * CA;
    xdot = [q/V*(CA0 - CA) - r;
            q/V*(T0 - T) - dH/(rho*Cp)*r + UA/(V*rho*Cp)*(Tc - T);
            u/Vc*(Tc0 - Tc) + UA/(Vc*rhoc*Cpc)*(T - Tc)];
end