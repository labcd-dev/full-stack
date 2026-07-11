function [inv_a, pinv_a, matrix_rank, solve_left, solve_right, U, S, V, chol_factor, V_eig, D_eig, V_eig_gen, D_eig_gen, V_eigs, D_eigs, Q, R, L, U_lu, P, regression] = linear_algebra(a, b, Z, y)
    inv_a = inv(a);
    pinv_a = pinv(a);
    matrix_rank = rank(a);
    % solve_left = a\b;
    % solve_right = b/a;
    [U, S, V] = svd(a);
    chol_factor = chol(a);
    [V_eig, D_eig] = eig(a);
    [V_eig_gen, D_eig_gen] = eig(a, b);
    [V_eigs, D_eigs] = eigs(a, 3);
    [Q, R] = qr(a, 0);
    [L, U_lu, P] = lu(a);
    regression = Z\y;
end