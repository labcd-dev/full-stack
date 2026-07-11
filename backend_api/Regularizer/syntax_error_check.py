import os
import ast
from typing import Dict, Any

from backend_api.Regularizer.MatlabToPython.matlab_to_numpy import get_defined_names


def get_code_context(code_lines: list, line_num: int, context_window: int = 1) -> str:
    """
    Helper function to extract code context around a specific line.
    Adds an arrow pointing to the exact line of the error.
    """
    if line_num == "Unknown" or not isinstance(line_num, int):
        return "Context unavailable."

    # Line numbers are 1-based, list indices are 0-based
    idx = line_num - 1
    start = max(0, idx - context_window)
    end = min(len(code_lines), idx + context_window + 1)

    context_str = []
    for i in range(start, end):
        # Visually flag the target line
        prefix = ">> " if i == idx else "   "
        context_str.append(f"{prefix}{i + 1}: {code_lines[i]}")

    return "\n".join(context_str)


class EOMStaticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.warnings = []

        # Scope and line tracking
        self.defined_names = set()
        self.used_names = set()
        self.name_to_line = {}

        # Track variables that are explicitly quantities, scalars, or vectors (NOT functions)
        self.local_variables = set()

    def visit_FunctionDef(self, node):
        """Track arguments defined in the EOM function signature."""
        for arg in node.args.args:
            self.defined_names.add(arg.arg)
            self.local_variables.add(arg.arg)  # Arguments like t, x, u are variables
            if arg.arg not in self.name_to_line:
                self.name_to_line[arg.arg] = node.lineno
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Track variables and validate assignment balance."""
        targets_count = 0
        values_count = 1

        lhs_names = []
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple):
            lhs_names = [elt.id for elt in node.targets[0].elts if isinstance(elt, ast.Name)]
            targets_count = len(lhs_names)
            for name in lhs_names:
                self.defined_names.add(name)
                self.local_variables.add(name)  # Unpacked items are variables
                if name not in self.name_to_line:
                    self.name_to_line[name] = node.lineno
        else:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined_names.add(target.id)
                    self.local_variables.add(target.id)  # Standard assignments are variables
                    if target.id not in self.name_to_line:
                        self.name_to_line[target.id] = node.lineno

        if targets_count > 0 and values_count > 1 and targets_count != values_count:
            self.errors.append({
                "Line": node.lineno,
                "Flag": "UnbalancedAssignment",
                "Message": f"Unbalanced Assignment Error! You are trying to unpack {values_count} values into {targets_count} variables."
            })

        self.generic_visit(node)

    def visit_Call(self, node):
        """Surgically intercept cases where variables are accidentally called as functions."""
        if isinstance(node.func, ast.Name):
            called_name = node.func.id

            # CRITICAL CHECK: If they are calling a known local numerical variable
            if called_name in self.local_variables:
                self.errors.append({
                    "Line": node.lineno,
                    "Flag": "TypeErrorRisk",
                    "Message": (
                        f"Type Error Risk: '{called_name}' is defined as a variable, but you are trying to call it "
                        f"like a function '{called_name}(...)'. This usually indicates a missing comma ',' in a list "
                        f"or a missing multiplication operator '*'."
                    )
                })

        self.generic_visit(node)

    def visit_Name(self, node):
        """Track variables that are read/used."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            if node.id not in self.name_to_line:
                self.name_to_line[node.id] = node.lineno
        self.generic_visit(node)

    def visit_Global(self, node):
        """Detect the use of the 'global' keyword."""
        self.errors.append({
            "Line": node.lineno,
            "Flag": "GlobalMutationRisk",
            "Message": f"Global Mutation Risk: Usage of 'global {', '.join(node.names)}' detected. EOM functions should be pure."
        })
        self.generic_visit(node)

    def visit_BinOp(self, node):
        """Detect standard multiplication to warn about potential matrix multiplication errors."""
        if isinstance(node.op, ast.Mult):
            self.warnings.append({
                "Line": node.lineno,
                "Flag": "MatrixMultiplicationRisk",
                "Message": "Standard multiplication '*' used. Verify if matrix multiplication '@' is required here."
            })
        self.generic_visit(node)


def analyze_static_eom(code_string: str) -> Dict[str, Any]:
    """
    Takes a string of Python/NumPy code and performs static analysis
    for syntax, scope, and mathematical operator warnings.
    """
    report = {
        "status": "PASS",
        "syntax_errors": [],
        "static_errors": [],
        "warnings": []
    }

    code_lines = code_string.splitlines()

    # 1. Syntax & Indentation Errors
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        report["status"] = "FAIL"
        report["syntax_errors"].append({
            "Line": e.lineno,
            "Flag": "SyntaxError",
            "Message": f"Syntax Error: {e.msg}",
            "Context": get_code_context(code_lines, e.lineno, context_window=3)
        })
        return report

    # 2. Run AST Traversal
    analyzer = EOMStaticAnalyzer()
    analyzer.visit(tree)

    # 3. NameErrors (Undefined Variables)
    undefined_vars = analyzer.used_names - analyzer.defined_names - get_defined_names()
    for var in undefined_vars:
        line_num = analyzer.name_to_line.get(var, "Unknown")
        analyzer.errors.append({
            "Line": line_num,
            "Flag": "UndefinedVariable",
            "Message": f"Undefined Variable: '{var}' is used but never explicitly defined or passed as an argument."
        })

    # 4. Unused Variables/Parameters
    unused_vars = analyzer.defined_names - analyzer.used_names
    for var in unused_vars:
        line_num = analyzer.name_to_line.get(var, "Unknown")
        analyzer.warnings.append({
            "Line": line_num,
            "Flag": "UnusedVariable",
            "Message": f"Unused Variable: '{var}' is defined but never used in the equations."
        })

    # 5. Populate final report and inject Context mapping
    for error in analyzer.errors:
        error["Context"] = get_code_context(code_lines, error["Line"], context_window=3)

    for warning in analyzer.warnings:
        warning["Context"] = get_code_context(code_lines, warning["Line"], context_window=3)

    report["static_errors"] = analyzer.errors
    report["warnings"] = analyzer.warnings

    if report["syntax_errors"] or report["static_errors"]:
        report["status"] = "FAIL"
    elif report["warnings"]:
        report["status"] = "PASS_WITH_WARNINGS"

    return report
