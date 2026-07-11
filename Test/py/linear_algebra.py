from numpy import *
import scipy.linalg as linalg

def linear_algebra(a, b, Z, y):
    inv_a = linalg.inv(a)
    pinv_a = linalg.pinv(a)
    matrix_rank = linalg.matrix_rank(a)
    # solve_left = linalg.solve(a, b)
    # solve_right = linalg.solve(a.T, b.T).T
    U, S, Vh = linalg.svd(a)
    V = Vh.T
    chol_factor = linalg.cholesky(a)
    D_eig, V_eig = linalg.eig(a)
    D_eig_gen, V_eig_gen = linalg.eig(a, b)
    D_eigs, V_eigs = linalg.eigs(a, k=3)
    Q, R = linalg.qr(a)
    P, L, U_lu = linalg.lu(a)
    regression = linalg.solve(Z, y)
    return inv_a, pinv_a, matrix_rank, solve_left, solve_right, U, S, V, chol_factor, V_eig, D_eig, V_eig_gen, D_eig_gen, V_eigs, D_eigs, Q, R, L, U_lu, P, regression