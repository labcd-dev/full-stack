function [vector_norm, log_and, log_or, bit_and, bit_or] = math_reductions(a, b, v)
    % max_global = max(max(a));
    % max_col = max(a);
    % max_row = max(a, [], 2);
    % max_elem_wise = max(a, b);
    vector_norm = norm(v);
    log_and = a & b;
    log_or = a | b;
    bit_and = bitand(a, b);
    bit_or = bitor(a, b);
end