# from helper_functions import *
from backend_core.Regularizer.MatlabToPython.helper_functions import *

SYNTAX_AND_MATH_RULES = [
    {'pattern': r'clear;', 'replacement': ''},
    {'pattern': r'close;', 'replacement': ''},
    {'pattern': r'close all;', 'replacement': ''},
    {'pattern': r'clc;', 'replacement': ''},
    {'pattern': r"\n'", 'replacement': "'"},
    {'pattern': r'\n"', 'replacement': '"'},
    {'pattern': r';\n', 'replacement': ';'},
    {'pattern': r';', 'replacement': ';\n'},
    {'pattern': r'\btrue\b', 'replacement': 'True'},
    {'pattern': r'\bfalse\b', 'replacement': 'False'},
    {'pattern': r'&&', 'replacement': 'and'},
    {'pattern': r'\|\|', 'replacement': 'or'},
    {'pattern': r'\belseif\b', 'replacement': 'elif'},
    {'pattern': r'\bbitand\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'replacement': r'\1 __BITWISE_AND__ \2'},
    {'pattern': r'\bbitor\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'replacement': r'\1 __BITWISE_OR__ \2'},
    {'pattern': r'\b(\w+)\s*&\s*(\w+)\b', 'replacement': r'logical_and(\1, \2)'},
    {'pattern': r'\b(\w+)\s*\|\s*(\w+)\b', 'replacement': r'logical_or(\1, \2)'},
    {'pattern': r'__BITWISE_AND__', 'replacement': '&'},
    {'pattern': r'__BITWISE_OR__', 'replacement': '|'},
    {'pattern': r'\.\*', 'replacement': '*'},
    {'pattern': r'\./', 'replacement': '/'},
    {'pattern': r'\.\^', 'replacement': '**'},
    {'pattern': r'\^', 'replacement': '**'},
    {'pattern': r'\bmax\(max\((.*?)\)\)', 'replacement': r'\1.max()'},
    {'pattern': r'\bmax\((.*?),\s*\[\],\s*2\)', 'replacement': r'\1.max(1)'},
    {'pattern': r'\breshape\(\s*(.*?)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', 'replacement': convert_reshape},
    {'pattern': r'\batan\b', 'replacement': 'arctan'},
    {'pattern': r'\batan2\b', 'replacement': 'arctan2'},
    {'pattern': r'\basin\b', 'replacement': 'arcsin'},
    {'pattern': r'\bacos\b', 'replacement': 'arccos'},
    {'pattern': r'\basinh\b', 'replacement': 'arcsinh'},
    {'pattern': r'\bacosh\b', 'replacement': 'arccosh'},
    {'pattern': r'\batanh\b', 'replacement': 'arctanh'},
    {'pattern': r'(?m)^(\s*)(\w+)\s*=\s*(?:\[\s*)?([^()\[\];\n]+:[^()\[\];\n]+)(?:\s*\])?(\.?\')?', 'replacement': replace_standalone_colon},
    {'pattern': r'(?m)^.*$', 'replacement': process_line_transposes},
    {'pattern': r'\brng\s*\(\s*(\d+|\w+)(?:\s*,\s*[\'"][^\'"]+[\'"])?\s*\)', 'replacement': r'rng = random.default_rng(\1)'},
    {'pattern': r'\brand\s*\(\s*([^)]+)\s*\)', 'replacement': r'rng.random((\1))'},
    {'pattern': r'\brepmat\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'replacement': r'tile(\1, (\2, \3))'},
    {'pattern': r'\bmeshgrid\s*\(\s*([^(),:]+):([^(),:]+)\s*,\s*([^(),:]+):([^(),:]+)\s*\)',
        'replacement': lambda m: f"meshgrid(r_[{m.group(1)}:{int(m.group(2))+1}.], r_[{m.group(3)}:{int(m.group(4))+1}.])" if m.group(1).strip().isdigit() and m.group(2).strip().isdigit() and m.group(3).strip().isdigit() and m.group(4).strip().isdigit() else f"meshgrid(r_[{m.group(1)}:{m.group(2)}+1.], r_[{m.group(3)}:{m.group(4)}+1.])"},
    {'pattern': r'\bsort\s*\(\s*([^,]+)\s*,\s*1\s*\)',  'replacement': r'sort(\1, axis=0)'},
    {'pattern': r'\bsort\s*\(\s*([^,]+)\s*,\s*2\s*\)', 'replacement': r'sort(\1, axis=1)'},
    {'pattern': r'\[\s*(\w+)\s*,\s*(\w+)\s*\]\s*=\s*sortrows\s*\(\s*([^,]+)\s*,\s*(\d+)\s*\)',
        'replacement': lambda m: f"{m.group(2)} = argsort({m.group(3)}[:, {int(m.group(4)) - 1}])\n{m.group(1)} = {m.group(3)}[{m.group(2)}, :]"},
]

SOLVER_RULES = [
    # Case 10: integral -> quad
    {'pattern': r'\bintegral\s*\(\s*@\(\s*(\w+)\s*\)\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)',
     'replacement': r'quad(lambda \1: \2, \3, \4)'},
    {'pattern': r'q\s*=\s*quad\(', 'replacement': 'q, _ = quad('},

    # Case 11: bvp4c
    {'pattern': r'\bbvp4c\s*\(\s*@(\w+)\s*,\s*@(\w+)\s*,\s*(\w+)\s*\)',
     'replacement': r'solve_bvp(\1, \2, \3.x, \3.y)'},

    # Case 5: fzero with args
    {'pattern': r'\bfzero\s*\(\s*@\(\s*(\w+)\s*\)\s*(\w+)\(\s*\1\s*,\s*([^)]+)\s*\)\s*,\s*([^)]+)\s*\)',
     'replacement': r'fsolve(\2, \4, args=(\3))[0]'},

    # Case 4: fsolve vectorized (Semicolon -> Comma flattens the array!)
    {'pattern': r'\bfsolve\s*\(\s*@\(\s*(\w+)\s*\)\s*(\[[^\]]+\])\s*,\s*(\[[^\]]+\])\s*\)',
     'replacement': lambda m: f"fsolve(lambda {m.group(1)}: {m.group(2).replace(';', ', ')}, {m.group(3).replace(';', ', ')})"},

    # Case 7: Systems of ODEs
    {'pattern': r'\[\s*(\w+)\s*,\s*(\w+)\s*\]\s*=\s*(ode45|ode15s)\s*\(\s*@\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*(\[[^\]]+\])\s*,\s*(\[[^\]]+\])\s*,\s*(\[[^\]]+\])\s*\);?',
     'replacement': lambda m: f"sol = solve_ivp(lambda {m.group(4)}, {m.group(5)}: {m.group(6).replace(';', ', ')}, {m.group(7).replace(';', ', ')}, {m.group(8).replace(';', ', ')}, method='{'Radau' if m.group(3) == 'ode15s' else 'RK45'}')\n{m.group(1)}, {m.group(2)} = sol.t, sol.y.T"},

    # Case 8: ODE with args
    {'pattern': r'\[\s*(\w+)\s*,\s*(\w+)\s*\]\s*=\s*(ode45|ode15s)\s*\(\s*@\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*(\w+)\(\s*\4\s*,\s*\5\s*,\s*([^)]+)\s*\)\s*,\s*([^,]+)\s*,\s*([^);]+)\s*\);?',
     'replacement': lambda m: f"sol = solve_ivp({m.group(6)}, {m.group(8)}, {m.group(9)}, args=({m.group(7)},), method='{'Radau' if m.group(3) == 'ode15s' else 'RK45'}')\n{m.group(1)}, {m.group(2)} = sol.t, sol.y.T"},

    # Case 6 & 9: Basic ODE
    {'pattern': r'\[\s*(\w+)\s*,\s*(\w+)\s*\]\s*=\s*(ode45|ode15s)\s*\(\s*@\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*([^,]+)\s*,\s*(\[[^\]]+\])\s*,\s*([^);]+)\s*\);?',
     'replacement': lambda m: f"sol = solve_ivp(lambda {m.group(4)}, {m.group(5)}: {m.group(6).replace(';', ', ')}, {m.group(7).replace(';', ', ')}, [{m.group(8).strip()}], method='{'Radau' if m.group(3) == 'ode15s' else 'RK45'}')\n{m.group(1)}, {m.group(2)} = sol.t, sol.y[0]"},

    # Roots & basic fzero
    {'pattern': r'\bfzero\s*\(\s*@\(\s*(\w+)\s*\)\s*([^,]+)\s*,\s*([^);]+)\s*\)', 'replacement': r'fsolve(lambda \1: \2, \3)[0]'},
    {'pattern': r'\bfzero\s*\(\s*@(\w+)\s*,\s*(\[[^\]]+\])\s*\)', 'replacement': r'fsolve(\1, \2)[0]'},
    {'pattern': r'\broots\s*\(\s*(\[[^\]]+\])\s*\)', 'replacement': r'roots(\1)'},
]

FILE_IO_RULES = [
    {'pattern': r'\bfopen\s*\(([^,]+),\s*([\'"])([^\'"]+)\2\s*\)', 'replacement': r'open(\1, \'\3\')'},
    {'pattern': r'\bfclose\s*\((\w+)\)', 'replacement': r'\1.close()'},
]

ARRAY_AND_LINALG_RULES = [
    {'pattern': r'\'[^\'\n]*\'|"[^"\n]*"|\b([a-zA-Z_]\w*)\s*\\\s*([^;\n#]+)',
        'replacement': lambda m: m.group(0) if m.group(1) is None else f"linalg.solve({m.group(1)}, {m.group(2)})"},
    {'pattern': r'\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]\s*=\s*(?<!\.)svd\s*\(\s*([^)]+)\s*\)', 'replacement': r'\1, \2, \3h = linalg.svd(\4)\n\3 = \3h.T'},
    {'pattern': r'\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]\s*=\s*(?<!\.)eig\s*\(\s*(.+?)\s*\)', 'replacement': r'\2, \1 = linalg.eig(\3)'},
    {'pattern': r'\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]\s*=\s*(?<!\.)eigs\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'replacement': r'\2, \1 = linalg.eigs(\3, k=\4)'},
    {'pattern': r'\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]\s*=\s*(?<!\.)qr\s*\(\s*([^,]+)\s*(?:,\s*0)?\s*\)', 'replacement': r'\1, \2 = linalg.qr(\3)'},
    {'pattern': r'\[\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\]\s*=\s*(?<!\.)lu\s*\(\s*([^)]+)\s*\)', 'replacement': r'\3, \1, \2 = linalg.lu(\4)'},
    {'pattern': r'(?<!\.)\bdet\s*\(\s*([^)]+)\s*\)', 'replacement': r'linalg.det(\1)'},
    {'pattern': r'(?<!\.)\binv\s*\(\s*([^)]+)\s*\)', 'replacement': r'linalg.inv(\1)'},
    {'pattern': r'(?<!\.)\bnorm\s*\(\s*([^)]+)\s*\)', 'replacement': r'linalg.norm(\1)'},
    {'pattern': r'(?<!\.)\beig\s*\(\s*([^)]+)\s*\)', 'replacement': r'linalg.eigvals(\1)'},
    {'pattern': r'(?<!\.)\bsvd\s*\(\s*([^)]+)\s*\)', 'replacement': r'linalg.svd(\1)'},
    {'pattern': r'\bsize\((.*?),\s*(\d+)\)', 'replacement': lambda m: f"{m.group(1)}.shape[{int(m.group(2)) - 1}]"},
    {'pattern': r'\bndims\((.*?)\)', 'replacement': r'ndim(\1)'},
    {'pattern': r'\bnumel\((.*?)\)', 'replacement': r'size(\1)'},
    {'pattern': r'\bsize\((.*?)\)', 'replacement': r'shape(\1)'},
    {'pattern': r'\brestrict\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'replacement': r'\1.reshape(\2, \3)'},
    {'pattern': r'\bzeros\((.*?)\)', 'replacement': r'zeros((\1))'},
    {'pattern': r'\bones\((.*?)\)', 'replacement': r'ones((\1))'},
    {'pattern': r'\beye\((.*?)\)', 'replacement': r'eye(\1)'},
    {'pattern': r'\bdiag\((.*?)\)', 'replacement': r'diag(\1)'},
    {'pattern': r'\blinspace\((.*?)\)', 'replacement': r'linspace(\1)'},
    {'pattern': r'(?<!\.)\bpinv\((.*?)\)', 'replacement': r'linalg.pinv(\1)'},
    {'pattern': r'(?<!\.)\bchol\((.*?)\)', 'replacement': r'linalg.cholesky(\1)'},
    {'pattern': r'(?<!\.)\brank\((.*?)\)', 'replacement': r'linalg.matrix_rank(\1)'},
    {'pattern': r'\bfft\((.*?)\)', 'replacement': r'fft.fft(\1)'},
    {'pattern': r'\bifft\((.*?)\)', 'replacement': r'fft.ifft(\1)'},
    {'pattern': r'\bsort\((.*?)\)', 'replacement': r'sort(\1)'},
    {'pattern': r'\bsqueeze\((.*?)\)', 'replacement': r'\1.squeeze()'},
    {'pattern': r'\bunique\((.*?)\)', 'replacement': r'unique(\1)'},
]

DISPLAY_AND_PLOTTING_RULES = [
    {'pattern': r'\bdisp\((.*?)\);?', 'replacement': r'print(\1)'},
    {'pattern': r'\bplot\((.*?)\);?', 'replacement': r'plt.plot(\1)'},
    {'pattern': r'\btitle\((.*?)\);?', 'replacement': r'plt.title(\1)'},
    {'pattern': r'\bxlabel\((.*?)\);?', 'replacement': r'plt.xlabel(\1)'},
    {'pattern': r'\bylabel\((.*?)\);?', 'replacement': r'plt.ylabel(\1)'},
    {'pattern': r'\bgrid\s+on\b;?', 'replacement': r'plt.grid(True)'},
    {'pattern': r'\bgrid\s+off\b;?', 'replacement': r'plt.grid(False)'},
]

CLEAN_FPLOT_RULES = [
    {'pattern': r'(\s*)\bfplot\(\s*@\s*\(\s*(\w+)\s*\)\s*(.*?),\s*\[\s*(.*?)\s*,\s*(.*?)\s*\]\);?', 'replacement': clean_fplot},
]

CONVERT_LHS_MATRIX ={'pattern': r'^(\s*)\[([^\]]+)\]\s*=\s*(.+)$','replacement': replacer}

CONVERT_INDEX_EXPR = {'pattern': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^()]*)\)', 'replacement': convert_index_expr,}

# For backward compatibility with the original load_rules function
RULES_DICT = {
    'syntax_and_math': SYNTAX_AND_MATH_RULES,
    'file_io': FILE_IO_RULES,
    'array_and_linalg': ARRAY_AND_LINALG_RULES,
    'display_and_plotting': DISPLAY_AND_PLOTTING_RULES,
    'clean_fplot_rules': CLEAN_FPLOT_RULES,
    'convert_lhs_matrix': CONVERT_LHS_MATRIX,
    'convert_index_expr': CONVERT_INDEX_EXPR,
    'solver_rules': SOLVER_RULES
}

if __name__ == '__main__':
    import numpy
    print(numpy.__all__)
    print(type(numpy.__all__))
    print(len(numpy.__all__))
    import builtins

    print(dir(builtins))
    print(type(dir(builtins)))
    print(len(dir(builtins)))

    import matplotlib.pyplot as plt
    print(dir(plt))
    print(type(dir(plt)))
    print(len(dir(plt)))