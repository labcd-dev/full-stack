function dxdt = system_dynamics(t, x, u)
% =========================================================================
% UNIVERSAL PLANT MODEL
% Target: MATLAB ode45 / Simulink
%
% Structure:
%   x = [state1; state2; ...; stateN]
%   u = [input1; input2; ...; inputM]
% =========================================================================

    %% 1. PARAMETERS (Hard-coded constants)
    % [LLM: Define all coefficients, mass, inertia, or gains here]
    % Example: mass = 10; gravity = 9.81;
    % [PARAM_START]

    % [PARAM_END]

    %% 2. UNPACK STATES & INPUTS
    % [LLM: Mapping for readability]
    % [UNPACK_START]
    % Example: pos = x(1); vel = x(2);
    % Example: force = u(1);

    % [UNPACK_END]

    %% 3. DYNAMICS / EQUATIONS OF MOTION
    % [LLM: Implement the differential equations]
    % If 2nd order: d_pos = vel; d_vel = (force - b*vel - k*pos)/m;
    % [EOM_START]

    % [EOM_END]

    %% 4. DERIVATIVE VECTOR CONSTRUCTION
    % [LLM: Must be a column vector matching the state order]
    % [DERIVATIVE_START]
    dxdt = [];
    % [DERIVATIVE_END]

end