clc;
clear;
close all;

% Create a sample matrix a (10x10 for demonstration)
a = reshape(1:100, 10, 10);
b = 1:101;
c = 1:0.1:10;
d = [1:10]
z2d = zeros(3,4);
z3d = zeros(3,4,5);
o2d = ones(3,4);
identity = eye(3);

% Transpose
aTrans = a.';
disp(aTrans);
aConjTrans = a';
disp(aConjTrans)
col_vec = [1:10]';

% Display original matrix
disp('Original matrix a:');
disp(a);

% 1. Last element (linear indexing)
disp('a(end):');
disp(a(end));

% 2. Element at row 2, column 5
disp('a(2,5):');
disp(a(2,5));

% 3. First 5 rows, all columns
disp('a(1:5,:):');
disp(a(1:5,:));

% 4. Last 5 rows, all columns
disp('a(end-4:end,:):');
disp(a(end-4:end,:));

% 5. Specific rows [2,4,5] and columns [1,3]
disp('a([2,4,5],[1,3]):');
disp(a([2,4,5],[1,3]));

% 6. Every other row from row 3 to row 21 (step 2)
disp('a(3:2:21,:):');
disp(a(3:2:10,:));

% 7. Every other row from first row
disp('a(1:2:end,:):');
disp(a(1:2:end,:));

% 8. Rows in reverse order
disp('a(end:-1:1,:):');
disp(a(end:-1:1,:));

% 9. Append a copy of the first row to the end (corrected syntax)
disp('a([1:end, 1],:):');
disp(a([1:end, 1],:));

%% 10. Define matrix
a = [1.02 3.04 5.06];
b = [ 1 2 3; 4 5 6 ];
c = [1.02 3.04 5.06];
d = [a; c];
e = [a c];
disp(d)
disp(e)
