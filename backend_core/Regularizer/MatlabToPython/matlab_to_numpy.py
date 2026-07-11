import re
import numpy
import builtins
import matplotlib.pyplot as plt

from backend_core.Regularizer.MatlabToPython.translation_rules import RULES_DICT


_user_functions = set()

def matlab_to_numpy(matlab_code: str) -> str:
    """
    Translates MATLAB syntax to Python/NumPy syntax based on the official
    'NumPy for MATLAB users' guide using a hybrid Python pipeline.
    """
    global _user_functions
    _user_functions.clear()
    py_code = matlab_code

    py_code = _regex_replacing_syntax(py_code, RULES_DICT)
    py_code = _code_reading_loop(py_code, RULES_DICT)
    py_code = _convert_matlab_arrays(py_code)
    py_code = _hoist_function_definitions(py_code)
    py_code = _final_clean_up(py_code)

    return py_code


def get_defined_names():
    defined_names = set(dir(builtins))
    defined_names.update(numpy.__all__)
    defined_names.update(dir(plt))
    defined_names.update(
        {'default_rng', 'det', 'inv', 'norm', 'eig', 'pinv', 'matrix_rank', 'svd', 'cholesky',
         'eigvals', 'eigs', 'qr', 'lu', 'lstsq', 'solve', 'fsolve', 'solve_ivp', 'solve_bvp', 'quad'})
    return defined_names


def _final_clean_up(py_code: str) -> str:
    all_imports = ""
    if "linalg." in py_code:
        all_imports += "import scipy.linalg as linalg\n"
    if "plt." in py_code and "plt.show()" not in py_code:
        py_code += "\nplt.show()"
        all_imports += "import matplotlib.pyplot as plt\n"
    if "fsolve" in py_code:
        all_imports += "from scipy.optimize import fsolve\n"
    if "solve_ivp" in py_code:
        all_imports += "from scipy.integrate import solve_ivp\n"
    if "quad(" in py_code:
        all_imports += "from scipy.integrate import quad\n"
    if "solve_bvp" in py_code:
        all_imports += "from scipy.integrate import solve_bvp\n"


    import_statements = "from numpy import *\n" + all_imports +"\n"
    py_code = import_statements + py_code

    # Clean up trailing semicolons on block endings
    py_code = re.sub(r';\s*$', '\n', py_code, flags=re.MULTILINE)

    # Comments: % to #
    py_code = re.sub(r'^\s*%', '#', py_code, flags=re.MULTILINE)
    py_code = re.sub(r'(?<!\\)%', '#', py_code)

    return py_code


def _hoist_function_definitions(py_code: str) -> str:
    """
    Finds all 'def ...' function definitions along with their bodies,
    removes them from their current positions, and moves them to the
    top of the script (just under the imports).
    """
    lines = py_code.splitlines()
    func_blocks = []
    main_code_lines = []

    in_func = False
    current_func = []

    for line in lines:
        stripped = line.strip()

        # Detect the start of a function block
        if line.startswith('def ') or (stripped.startswith('def ') and in_func is False):
            in_func = True
            current_func.append(line)
            continue

        if in_func:
            # If line is completely empty or just a comment at indentation 0,
            # it might be the end of the function. Let's look closely at non-empty structural code.
            if line.startswith(' ') or line.startswith('\t') or not stripped:
                current_func.append(line)
            elif stripped.startswith('#'):
                # Keep comments inside or directly trailing if indented
                current_func.append(line)
            else:
                # Reached a structural line at indentation 0 -> Function ended.
                in_func = False
                func_blocks.append('\n'.join(current_func))
                current_func = []
                main_code_lines.append(line)
        else:
            main_code_lines.append(line)

    # Catch any remaining function if it was at the very end of the file
    if in_func and current_func:
        func_blocks.append('\n'.join(current_func))

    # Reconstruct the code
    hoisted_functions = '\n\n'.join(func_blocks)
    remaining_code = '\n'.join(main_code_lines)

    # Strip excess structural spaces but maintain spacing layout
    if hoisted_functions:
        return f"{hoisted_functions}\n\n{remaining_code}"
    return remaining_code


def _apply_python_rules(code: str, rules_list: list) -> str:
    """Sequentially executes basic regex pattern replacements extracted from Python rules."""
    if not rules_list:
        return code
    for rule in rules_list:
        pattern = rule['pattern']
        replacement = rule['replacement']
        code = re.sub(pattern, replacement, code)

    return code


def _regex_replacing_syntax(py_code: str, rules: dict) -> str:
    """Dispatches the syntax modification pipeline steps across code regions."""
    py_code = re.sub(r'\.\.\..*?(\n|$)', ' ', py_code)

    py_code = _apply_python_rules(py_code, rules.get('syntax_and_math', []))
    py_code = _apply_python_rules(py_code, rules.get('solver_rules', []))
    py_code = _apply_python_rules(py_code, rules.get('file_io', []))
    py_code = _apply_python_rules(py_code, rules.get('array_and_linalg', []))
    py_code = _apply_python_rules(py_code, rules.get('display_and_plotting', []))
    py_code = _convert_fprintf_in_code(py_code)
    # The duplicate solver_rules call that was here is now gone!
    return py_code


def _code_reading_loop(code: str, rules) -> str:
    lines = code.splitlines()
    processed_lines = []
    processed_lines_2 = []
    return_stack = []
    indent_level = 0

    lhs_pattern = rules['convert_lhs_matrix']['pattern']
    lhs_replacement = rules['convert_lhs_matrix']['replacement']
    index_expr_pattern = rules['convert_index_expr']['pattern']
    index_expr_replacement = rules['convert_index_expr']['replacement']

    for line in lines:
        stripped_line = line.strip()
        line = _convert_lhs_matrix_assignment(stripped_line, lhs_pattern, lhs_replacement)
        line, processed_lines, indent_level = _convert_indexing_and_blocks(line, processed_lines, return_stack, indent_level)
        processed_lines.append(line)

    for line in processed_lines:
        line = _convert_matlab_indexing(line, index_expr_pattern, index_expr_replacement)
        processed_lines_2.append(line)

    return '\n'.join(processed_lines_2)


def _convert_matlab_indexing(line, pattern, convert_index_expr) -> str:
    known_functions = get_defined_names()
    known_functions.update(_user_functions)


    if line.startswith('#') or line.startswith('def '):
        return line

    modified = line
    pos = 0
    while True:
        match = re.search(pattern, modified[pos:])
        if not match:
            break
        start, end = match.span()
        full_start = pos + start
        full_end = pos + end
        var = match.group(1)
        inner = match.group(2)
        if var in known_functions:
            pos = full_end
            continue

        index_parts = []
        depth = 0
        current = []
        for ch in inner:
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
            elif ch == ',' and depth == 0:
                index_parts.append(''.join(current).strip())
                current = []
                continue
            current.append(ch)
        if current:
            index_parts.append(''.join(current).strip())

        # Pass array name and dimension information to the converter
        converted_parts = [convert_index_expr(part, var, i, len(index_parts)) for i, part in enumerate(index_parts)]

        # Only use ix_ if there are >= 2 array indices and NO slices are present
        adv_indices = [p for p in converted_parts if p.startswith('[') or p.startswith('r_[')]
        has_slice = any(':' in p for p in converted_parts if not (p.startswith('[') or p.startswith('r_[')))

        if len(adv_indices) >= 2 and not has_slice:
            new_index = f"ix_({', '.join(converted_parts)})"
        else:
            new_index = ', '.join(converted_parts)

        replacement = f"{var}[{new_index}]"
        modified = modified[:full_start] + replacement + modified[full_end:]
        pos = full_start + len(replacement)

    return modified



def _convert_indexing_and_blocks(stripped_line, processed_lines, return_stack, indent_level):
    spaces_per_level = 4

    # Normalize line by removing trailing semicolons, colons, and extra spaces
    norm_line = stripped_line.rstrip(';: ').strip()

    # 1. Handle Closing Blocks & Multiple Return Statement Generation
    if norm_line == 'end':
        indented_line = ""
        if return_stack and return_stack[-1]['depth'] == indent_level:
            ret_info = return_stack.pop()
            if ret_info['var']:
                # Clean up multiple outputs: e.g., "a, b, c"
                # MATLAB allows spaces or commas: [a b c] or [a, b, c]
                raw_vars = ret_info['var'].replace('[', '').replace(']', '')
                # Normalize spaces/commas to a clean comma-separated list
                vars_list = [v.strip() for v in re.split(r'[\s,]+', raw_vars) if v.strip()]
                python_return_val = ", ".join(vars_list)

                ret_indent = " " * (indent_level * spaces_per_level)
                indented_line = f"{ret_indent}return {python_return_val}"

        indent_level = max(0, indent_level - 1)
        return indented_line, processed_lines, indent_level

    # 2. Apply current line indentation for default fallback
    current_indent = " " * (indent_level * spaces_per_level)
    indented_line = current_indent + stripped_line if stripped_line else ""

    # 3. Handle Opening Blocks: Function Definitions (Single or Multiple Outputs)
    if norm_line.startswith('function '):
        # Matches: function [a, b] = name(x)  OR  function single_out = name(x)
        func_match = re.match(r'^function\s+(?:(\[.*?\]|\w+)\s*=\s*)?(\w+)\((.*?)\)', norm_line)
        if func_match:
            ret_val = func_match.group(1).strip() if func_match.group(1) else None
            func_name = func_match.group(2)
            args = func_match.group(3)

            # Python standard definitions don't declare return types in the signature
            indented_line = f"{current_indent}def {func_name}({args}):"

            # Adding function name to list of user function so it doesn't confuse it with an array
            _user_functions.add(func_name)

            indent_level += 1
            return_stack.append({'depth': indent_level, 'var': ret_val})
            return indented_line, processed_lines, indent_level

    # 4. Handle Opening Blocks: For Loops
    elif norm_line.startswith('for '):
        for_match = re.match(r'^for\s+(\w+)\s*=\s*(.*?)\s*$', norm_line)
        if for_match:
            loop_var = for_match.group(1)
            range_expr = for_match.group(2)
            parts = [p.strip() for p in range_expr.split(':')]

            if len(parts) == 2:
                start, stop = parts[0], parts[1]
                try:
                    stop_val = str(int(stop) + 1)
                except ValueError:
                    stop_val = f"{stop} + 1"
                indented_line = f"{current_indent}for {loop_var} in range({start}, {stop_val}):"

            elif len(parts) == 3:
                start, step, stop = parts[0], parts[1], parts[2]
                try:
                    stop_val = str(int(stop) + 1)
                except ValueError:
                    stop_val = f"{stop} + 1"
                indented_line = f"{current_indent}for {loop_var} in range({start}, {stop_val}, {step}):"
            else:
                indented_line = f"{current_indent}for {loop_var} in {range_expr}:"

            indent_level += 1
            return indented_line, processed_lines, indent_level

    # 5. Handle If Statements
    elif norm_line.startswith('if '):
        condition = norm_line[3:].strip()
        indented_line = f"{current_indent}if {condition}:"
        indent_level += 1
        return indented_line, processed_lines, indent_level

    # 6. Handle Elseif -> Elif (Checks both 'elseif' and pre-converted 'elif')
    elif norm_line.startswith('elseif ') or norm_line.startswith('elif '):
        prefix_len = 7 if norm_line.startswith('elseif ') else 5
        condition = norm_line[prefix_len:].strip()
        base_indent = " " * ((indent_level - 1) * spaces_per_level)
        indented_line = f"{base_indent}elif {condition}:"
        return indented_line, processed_lines, indent_level

    # 7. Handle Else
    elif norm_line == 'else':
        base_indent = " " * ((indent_level - 1) * spaces_per_level)
        indented_line = f"{base_indent}else:"
        return indented_line, processed_lines, indent_level

    # 8. Handle While Loops
    elif norm_line.startswith('while '):
        condition = norm_line[6:].strip()
        indented_line = f"{current_indent}while {condition}:"
        indent_level += 1
        return indented_line, processed_lines, indent_level

    # 9. Return for normal lines (non-block lines)
    return indented_line, processed_lines, indent_level


def _convert_lhs_matrix_assignment(line, lhs_pattern, lhs_replacement) -> str:
    # Only transform if the line is not inside a comment and has the pattern
    if not line.startswith('#') and re.search(lhs_pattern, line, re.MULTILINE):
        line = re.sub(lhs_pattern, lhs_replacement, line, flags=re.MULTILINE)
    return line


def _convert_fprintf_in_code(code: str) -> str:
    result = []
    i = 0
    while i < len(code):
        match = re.search(r'\bfprintf\s*\(', code[i:])
        if not match:
            result.append(code[i:])
            break

        start_idx = i + match.start()
        content_start = i + match.end()
        result.append(code[i:start_idx])

        # Find the matching closing parenthesis
        paren_depth = 1
        content_end = content_start
        while content_end < len(code) and paren_depth > 0:
            if code[content_end] == '(':
                paren_depth += 1
            elif code[content_end] == ')':
                paren_depth -= 1
            content_end += 1

        if paren_depth != 0:
            # Unmatched – keep as is
            result.append(code[start_idx:start_idx+1])
            i = start_idx + 1
            continue

        inner = code[content_start:content_end-1]

        # ----- parse arguments: handle optional fileID -----
        # Split by commas, respecting parentheses/brackets
        args = []
        cur = []
        depth = 0
        for ch in inner:
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            if ch == ',' and depth == 0:
                args.append(''.join(cur).strip())
                cur = []
            else:
                cur.append(ch)
        if cur:
            args.append(''.join(cur).strip())

        if not args:
            result.append(f"print({inner})")
            i = content_end
            continue

        # Decide: console (no fileID) or file output
        first_arg = args[0].strip()
        # If the first argument looks like a string literal -> console fprintf
        if (first_arg[0] in '"\'' and first_arg[0] == first_arg[-1]) or first_arg.startswith('f"'):
            # console: fprintf(format, ...)
            fmt_str = args[0]
            data_args = args[1:]
            target = "print"
        else:
            # file output: fprintf(fileID, format, ...)
            if len(args) < 2:
                # malformed, fallback
                result.append(f"print({inner})")
                i = content_end
                continue
            fmt_str = args[1]
            data_args = args[2:]
            target = f"{first_arg}.write"

        # ----- convert format string to f‑string -----
        # Extract quoted string content
        qmatch = re.match(r'^\s*([\'"])(.*?)\1\s*$', fmt_str, re.DOTALL)
        if not qmatch:
            # Not a proper string literal – fallback
            if target == "print":
                result.append(f"print({fmt_str}, {', '.join(data_args)})")
            else:
                result.append(f"{target}({fmt_str} % ({', '.join(data_args)}))")
            i = content_end
            continue

        quote = qmatch.group(1)
        raw_fmt = qmatch.group(2).replace(r'\n', '').replace('\\n', '')

        # Build the f‑string body by replacing %-specifiers with {var}
        var_index = 0
        def replacer(m):
            nonlocal var_index
            if var_index < len(data_args):
                v = data_args[var_index]
                var_index += 1
                return f"{{{v}}}"
            return m.group(0)   # keep original if no argument

        # Match printf specifiers: %[flags][width][.precision]type
        f_string_body = re.sub(r'%[-+ 0]*\d*\.?\d*[idfegs]', replacer, raw_fmt)
        f_string_lit = f"{quote}{f_string_body}{quote}"

        if target == "print":
            result.append(f"print(f{f_string_lit})")
        else:
            result.append(f"{target}(f{f_string_lit})")

        # Skip trailing semicolon
        j = content_end
        while j < len(code) and code[j] in ' \t':
            j += 1
        if j < len(code) and code[j] == ';':
            j += 1
        i = j

    return ''.join(result)


def _convert_matlab_arrays(code: str) -> str:
    """
    Convert MATLAB matrix/vector literals to NumPy array syntax.
    """
    result = []
    i = 0
    n = len(code)

    while i < n:
        if code[i] != '[':
            result.append(code[i])
            i += 1
            continue

        is_matrix_literal = True
        if i > 0:
            prev_char = code[i - 1]
            if prev_char.isalnum() or prev_char == '_' or prev_char == ')' or prev_char == ']' or prev_char in "\"\'":
                is_matrix_literal = False
            if prev_char in '(,':
                context = code[max(0, i - 20):i]
                if "meshgrid" in context:
                    is_matrix_literal = False

        if not is_matrix_literal:
            result.append(code[i])
            i += 1
            continue

        start = i
        bracket_count = 1
        j = i + 1
        while j < n and bracket_count > 0:
            if code[j] == '[':
                bracket_count += 1
            elif code[j] == ']':
                bracket_count -= 1
            j += 1

        if bracket_count != 0:
            result.append(code[i])
            i += 1
            continue

        matrix_content = code[i + 1:j - 1]
        np_array_str = _matrix_literal_to_numpy(matrix_content)
        result.append(np_array_str)
        i = j

    py_code = ''.join(result)

    # Post-processing scalar optimization REMOVED. Handled by Regex now.
    return py_code


def _matrix_literal_to_numpy(content: str) -> str:
    """
    Convert the inside of a MATLAB matrix literal (without brackets)
    to a string representing array([[...]]).
    """
    content = content.strip()
    if not content:
        return "array([])"

    # Split into rows using semicolons
    rows = []
    current_row = []
    paren_depth = 0
    bracket_depth = 0
    row_buffer = []

    for ch in content:
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth -= 1
        elif ch == '[':
            bracket_depth += 1
        elif ch == ']':
            bracket_depth -= 1
        elif ch == ';' and paren_depth == 0 and bracket_depth == 0:
            rows.append(''.join(row_buffer).strip())
            row_buffer = []
            continue
        row_buffer.append(ch)
    if row_buffer:
        rows.append(''.join(row_buffer).strip())

    # If only one row and no semicolon, it's a row vector (or scalar)
    if len(rows) == 1:
        elements = _split_row_elements(rows[0])
        return f"array([{', '.join(elements)}])"
    else:
        # Matrix with multiple rows
        matrix_rows = []
        for row in rows:
            elements = _split_row_elements(row)
            matrix_rows.append(f"[{', '.join(elements)}]")
        return f"array([{', '.join(matrix_rows)}])"


def _split_row_elements(row_str: str) -> list:
    r"""
    Split a row string...
    Does NOT split on whitespace that is adjacent to an operator (+, -, *, /, ^, \).
    """
    # Operators that, when adjacent to whitespace, indicate the whitespace is part of an expression
    operators = set('+-*/^\\')
    operators.add('.*')
    operators.add('./')


    elements = []
    current = []
    paren_depth = 0
    bracket_depth = 0

    i = 0
    n = len(row_str)
    while i < n:
        ch = row_str[i]

        # Track nesting
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth -= 1
        elif ch == '[':
            bracket_depth += 1
        elif ch == ']':
            bracket_depth -= 1

        # Check for delimiter (comma or whitespace) at depth zero
        if (ch == ',' or ch.isspace()) and paren_depth == 0 and bracket_depth == 0:
            # For whitespace, decide if it's a real delimiter or part of an operator expression
            is_real_delim = True
            if ch.isspace():
                # Look at the character before and after the whitespace
                prev_ch = row_str[i-1] if i > 0 else ''
                next_ch = row_str[i+1] if i+1 < n else ''
                # If either adjacent char is an operator, treat whitespace as part of expression (no split)
                if prev_ch in operators or next_ch in operators:
                    is_real_delim = False

            if is_real_delim:
                if current:
                    elements.append(''.join(current).strip())
                    current = []
                i += 1
                continue
            # else: whitespace is part of expression, fall through to append it

        current.append(ch)
        i += 1

    if current:
        elements.append(''.join(current).strip())
    # Filter out empty strings (e.g., trailing spaces)
    return [e for e in elements if e]

if __name__ == '__main__':
    matlab_input = """
function xdot = quadcopter_dynamics(t,x,omega)
X     = x(1);
Y     = x(2);
Z     = x(3);

u     = x(4);
v     = x(5);
w     = x(6);

phi   = x(7);
theta = x(8);
psi   = x(9);

p     = x(10);
q     = x(11);
r     = x(12);

m  = 1.5;
g  = 9.81;

Ix = 0.02;
Iy = 0.02;
Iz = 0.04;

l  = 0.25;      

kf = 1.2e-5;    
km = 2.4e-7;     

Cd = 0.1;     


w1 = omega(1);
w2 = omega(2);
w3 = omega(3);
w4 = omega(4);

F1 = kf*w1^2;
F2 = kf*w2^2;
F3 = kf*w3^2;
F4 = kf*w4^2;

T = F1 + F2 + F3 + F4;


tau_phi = l*(F2 - F4);

tau_theta = l*(F3 - F1);

tau_psi = km*( ...
     w1^2 ...
   - w2^2 ...
   + w3^2 ...
   - w4^2 );

tau = [tau_phi; tau_theta; tau_psi];

%% Rotation matrix

cphi = cos(phi);
sphi = sin(phi);

cth = cos(theta);
sth = sin(theta);

cps = cos(psi);
sps = sin(psi);

R = [...
cth*cps, ...
sphi*sth*cps-cphi*sps, ...
cphi*sth*cps+sphi*sps;

cth*sps, ...
sphi*sth*sps+cphi*cps, ...
cphi*sth*sps-sphi*cps;

-sth, ...
sphi*cth, ...
cphi*cth];

%% Position dynamics

vel_inertial = R*[u;v;w];

Xdot = vel_inertial(1);
Ydot = vel_inertial(2);
Zdot = vel_inertial(3);

Vb = [u;v;w];

omega_b = [p;q;r];

Fg_body = R'*[0;0;m*g];

Fthrust_body = [0;0;-T];

Fdrag = -Cd*Vb;

acc_body = ...
    (1/m)*(Fthrust_body + Fdrag + Fg_body) ...
    - cross(omega_b,Vb);

udot = acc_body(1);
vdot = acc_body(2);
wdot = acc_body(3);

%% Euler angle kinematics

E = [...
1, sin(phi)*tan(theta), cos(phi)*tan(theta);

0, cos(phi), -sin(phi);

0, sin(phi)/cos(theta), cos(phi)/cos(theta)];

eulerdot = E*omega_b;

phidot   = eulerdot(1);
thetadot = eulerdot(2);
psidot   = eulerdot(3);

%% Rotational dynamics

I = diag([Ix Iy Iz]);

omega_dot = I \ ...
    (tau - cross(omega_b,I*omega_b));

pdot = omega_dot(1);
qdot = omega_dot(2);
rdot = omega_dot(3);

%% Assemble state derivative

xdot = [...
    Xdot;
    Ydot;
    Zdot;
    udot;
    vdot;
    wdot;
    phidot;
    thetadot;
    psidot;
    pdot;
    qdot;
    rdot];
end
    """

    print(matlab_to_numpy(matlab_input))