% =========================================================================
% MATLAB Test File for Translation Application
% =========================================================================

clear;
clc;
close all;

%% 1. Matrix literals and Concatenation
% Testing 1D vectors and multi-dimensional matrices
a = [1.02 3.04 5.06];
b = [1 2 3; 4 5 6];
c = [1.02 3.04 5.06];

% Testing horizontal and vertical concatenation of variables
d = [a; c];
e = [a c];

disp('Matrix d:');
disp(d);
disp('Matrix e:');
disp(e);

%% 2. Basic Math and Syntax Rounding
fprintf('Rounded array a:\n');
disp(round(a));

%% 3. Conditional Blocks and Custom Functions
% This section tests function scoping, indentation, and elseif conversion
[x_val, y_val] = compute_metrics(10, 20);
[x_zero, y_zero] = compute_metrics(5, 5);

%% 4. Loops and Iterative Execution
% Testing for loops, step index limits, and nested while loops
for i = 1:3
    while i < 2
        disp('Nested execution active');
        i = i + 2;
    end
end

% MATLAB while loop example
counter = 1;
total = 0;

while counter <= 5
total = total + counter;
fprintf('Iteration %d: Sum = %d\n', counter, total);
counter = counter + 1;
end

fprintf('Final total: %d\n', total);

%% 5. Visualization Rules
% Basic grid and plotting functionality tests
x_axis = [1, 2, 3, 4, 5];
y_axis = [2, 4, 1, 5, 3];

plot(x_axis, y_axis);
title('Application Conversion Test Plot');
xlabel('X Coordinates');
ylabel('Y Coordinates');
grid on;

% =========================================================================
% Local Function Definitions
% =========================================================================
function [out1, out2] = compute_metrics(val1, val2)
    if val1 > val2
        out1 = val1;
        out2 = val2;
    elseif val1 == val2
        out1 = 0;
        out2 = 0;
    else
        out1 = val2;
        out2 = val1;
    end
end
