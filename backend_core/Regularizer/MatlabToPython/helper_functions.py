import re


def process_line_transposes(match):
    """
    Intelligently parses a line to convert MATLAB transposes (.' and ')
    to NumPy (.transpose() and .conj().transpose()) while completely ignoring string contents.
    """
    line = match.group(0)
    if "'" not in line:
        return line

    result = []
    i = 0
    n = len(line)
    in_string = False
    string_char = None

    while i < n:
        ch = line[i]

        if ch in '"\'':
            if not in_string:
                is_transpose = False
                # A single quote is a transpose if preceded by an alphanumeric, or closing brackets/dots
                if ch == "'":
                    if i > 0:
                        prev_ch = line[i - 1]
                        if prev_ch.isalnum() or prev_ch in '_)]}.':
                            is_transpose = True

                if is_transpose:
                    # Check if it's the non-conjugate transpose (.')
                    if i > 0 and line[i - 1] == '.':
                        result.pop()  # Remove the dot we already appended
                        result.append(".transpose()")
                    else:
                        result.append(".conj().transpose()")
                else:
                    # It's the start of a string
                    in_string = True
                    string_char = ch
                    result.append(ch)
            else:
                # We are in a string. Check if it's closing.
                if ch == string_char:
                    # Check for escaped quotes (e.g., 'It''s')
                    if i + 1 < n and line[i + 1] == string_char:
                        result.append(ch)
                        result.append(ch)
                        i += 1  # Skip next quote
                    else:
                        in_string = False  # String closed
                        result.append(ch)
                else:
                    result.append(ch)
        else:
            result.append(ch)
        i += 1

    return ''.join(result)


def convert_colon_to_arange(colon_str: str) -> str:
    """
    Converts a standalone MATLAB colon range expression (e.g., '1:10' or '0:0.1:1')
    into a NumPy 'arange' function call.
    """
    parts = [p.strip() for p in colon_str.split(':')]

    if len(parts) == 2:
        start, stop = parts[0], parts[1]
        # Inclusive range adjustment for integers vs variables/floats
        if start.isdigit() and stop.isdigit():
            return f"arange({start}, {int(stop) + 1})"
        return f"arange({start}, {stop} + 1)"

    elif len(parts) == 3:
        start, step, stop = parts[0], parts[1], parts[2]
        # To make arange inclusive of 'stop' like MATLAB, we add 'step' to 'stop'
        return f"arange({start}, {stop} + {step}, {step})"

    return colon_str


def replace_standalone_colon(match):
    """Regex callback to re-assemble the variable assignment line."""
    indent = match.group(1) or ""
    var_name = match.group(2).strip()
    colon_expr = match.group(3).strip()
    transpose_op = match.group(4)  # Captures the optional ' or .'

    base_expr = convert_colon_to_arange(colon_expr)

    # If a transpose operator was attached to the vector, reshape it vertically
    if transpose_op:
        return f"{indent}{var_name} = {base_expr}[:, newaxis]"
    return f"{indent}{var_name} = {base_expr}"


def convert_reshape(match):
    # match groups: leading whitespace? Actually pattern will capture full line or just the call.
    # We capture the entire reshape call parts.
    # Pattern: reshape( expr, rows, cols )
    array_expr = match.group(1).strip()
    rows = match.group(2)
    cols = match.group(3)

    # If the array expression contains a colon like "1:100", convert it
    colon_match = re.search(r'(\d+)\s*:\s*(\d+)', array_expr)
    if colon_match:
        start = colon_match.group(1)
        stop = colon_match.group(2)
        # Replace the whole array_expr with np.arange(start, stop+1)
        array_expr = f"arange({start}, {int(stop) + 1})"

    return f"reshape({array_expr}, ({rows}, {cols}), order='F')"


def clean_fplot(match):
    leading_space, var, expr, start, stop = match.groups()
    local_array = f"_{var}_vals"
    python_expr = re.sub(rf'\b{var}\b', local_array, expr)

    # Apply the matching leading whitespace to BOTH generated lines
    return (
        f"{leading_space}{local_array} = linspace({start}, {stop}, 1000)\n"
        f"{leading_space}plt.plot({local_array}, {python_expr})"
    )


def replacer(match):
    indent = match.group(1)
    var_list_raw = match.group(2)
    rhs = match.group(3)
    # Split variables: commas or whitespace
    vars_clean = re.split(r'[\s,]+', var_list_raw.strip())
    vars_clean = [v for v in vars_clean if v]
    lhs_comma = ', '.join(vars_clean)
    return f"{indent}{lhs_comma} = {rhs}"


def convert_index_expr(expr: str, arr_name: str = "", dim: int = 0, total_dims: int = 1) -> str:
    import re
    expr = expr.strip()
    if expr == "":
        return ":"

    # Helper: replace 'end' with contextual array dimension shape
    def _replace_end(s: str, allow_empty: bool = False) -> str:
        s = s.strip()
        if allow_empty and s == 'end':
            return ''

        shape_str = f"{arr_name}.shape[{dim}]" if total_dims > 1 else f"size({arr_name})"
        return re.sub(r'\bend\b', shape_str, s)

    # ---- Handle vector indices like [2,4,5] or [1:end, 1] ----
    if expr.startswith('[') and expr.endswith(']'):
        inner = expr[1:-1]
        parts = []
        cur = []
        depth = 0
        in_str = False
        quote_char = None
        for ch in inner:
            if ch in '"\'' and not in_str:
                in_str = True
                quote_char = ch
            elif in_str and ch == quote_char:
                in_str = False
            elif not in_str and ch in '([{':
                depth += 1
            elif not in_str and ch in ')]}':
                depth -= 1
            elif ch == ',' and depth == 0 and not in_str:
                parts.append(''.join(cur).strip())
                cur = []
                continue
            cur.append(ch)
        if cur:
            parts.append(''.join(cur).strip())

        has_colon = any(':' in p for p in parts)
        inner_args = []

        for part in parts:
            if ':' in part:
                colon_parts = part.split(':')
                if len(colon_parts) == 2:
                    start = colon_parts[0].strip()
                    stop = colon_parts[1].strip()
                    start_repl = _replace_end(start, False)
                    stop_repl = _replace_end(stop, False)
                    if start_repl.lstrip('-').isdigit() and start_repl != '-1':
                        start_repl = str(int(start_repl) - 1)
                    slice_str = f"{start_repl}:{stop_repl}" if stop_repl else f"{start_repl}:"
                    inner_args.append(slice_str)
                elif len(colon_parts) == 3:
                    start, step, stop = colon_parts
                    start_repl = _replace_end(start.strip(), False)
                    step_repl = _replace_end(step.strip(), False)
                    stop_repl = _replace_end(stop.strip(), False)
                    if start_repl.lstrip('-').isdigit() and start_repl != '-1':
                        start_repl = str(int(start_repl) - 1)
                    slice_str = f"{start_repl}:{stop_repl}:{step_repl}" if stop_repl else f"{start_repl}::{step_repl}"
                    inner_args.append(slice_str)
                else:
                    inner_args.append(part)
            else:
                if part == 'end':
                    shape_str = f"{arr_name}.shape[{dim}]" if total_dims > 1 else f"size({arr_name})"
                    inner_args.append(f"{shape_str} - 1")
                elif part.isdigit():
                    inner_args.append(str(int(part) - 1))
                else:
                    inner_args.append(_replace_end(part, False))

        if has_colon:
            return f"r_[{', '.join(inner_args)}]"
        else:
            return f"[{', '.join(inner_args)}]"

    # ---- Handle colon expressions (without outer brackets) ----
    if ':' in expr:
        parts = expr.split(':')
        if len(parts) == 2:
            start_raw, stop_raw = parts[0].strip(), parts[1].strip()
            start = _replace_end(start_raw, allow_empty=True)
            stop = _replace_end(stop_raw, allow_empty=True)

            if start_raw.isdigit():
                start = str(int(start_raw) - 1)

            if stop_raw == 'end':
                stop = ''
            elif stop_raw.isdigit():
                stop = stop_raw

            return f"{start}:{stop}" if stop else f"{start}:"

        elif len(parts) == 3:
            start_raw, step_raw, stop_raw = parts[0].strip(), parts[1].strip(), parts[2].strip()
            start = _replace_end(start_raw, allow_empty=True)
            step = _replace_end(step_raw, allow_empty=False)

            if start_raw.isdigit():
                start = str(int(start_raw) - 1)

            if stop_raw == 'end':
                stop = ''
            elif stop_raw.isdigit():
                # Correctly handle reversed step ranges
                is_negative = False
                try:
                    if int(step) < 0: is_negative = True
                except ValueError:
                    if step.startswith('-'): is_negative = True

                if is_negative:
                    if stop_raw == '1':
                        stop = ''
                    else:
                        stop = str(int(stop_raw) - 2)
                else:
                    stop = stop_raw
            else:
                stop = _replace_end(stop_raw, allow_empty=False)

            return f"{start}:{stop}:{step}" if (stop or step != '1') else f"{start}:"
        else:
            return expr

    # ---- Single element or expression ----
    if expr == 'end':
        return '-1'
    if expr.isdigit():
        return str(int(expr) - 1)
    if 'end' in expr:
        return _replace_end(expr, allow_empty=False)
    return expr