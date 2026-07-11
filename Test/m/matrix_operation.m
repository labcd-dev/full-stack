function [horiz_cat, vert_cat, sorted_cols, sorted_rows, sorted_rows_array, I, unsqueezed, row, corner] = matrix_operations(a, b, M)
    % horiz_cat = [a b];
    % vert_cat = [a; b];
    sorted_cols = sort(a);
    sorted_rows = sort(a, 2);
    [sorted_rows_array, I] = sortrows(a, 1);
    unsqueezed = squeeze(a);
    row = M(2, :);
    corner = M(end, end);
end