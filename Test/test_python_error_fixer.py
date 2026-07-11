import ast
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now this import will resolve perfectly
from backend_api.Regularizer.fix_syntax_error import fix_code

M_DIR = PROJECT_ROOT / "test/corrupted_py"
PY_DIR = PROJECT_ROOT / "test/fixed_py"

import ast


class FlattenTupleAssignments(ast.NodeTransformer):
    """
    Transforms `a, b = (1, 2)` into:
    a = 1
    b = 2
    so the AST looks identical to sequential assignment.
    """

    def visit_Assign(self, node):
        # Check if it's a tuple assignment like: x, y = (1, 2)
        if isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple):
            targets = node.targets[0].elts
            values = node.value.elts

            # If the number of variables matches the number of values
            if len(targets) == len(values):
                new_nodes = []
                for target, value in zip(targets, values):
                    # Create an individual ast.Assign node for each pair
                    new_nodes.append(ast.Assign(targets=[target], value=value))
                return new_nodes
        return node


def normalize_python_code(code_string):
    try:
        parsed_ast = ast.parse(code_string)

        # Apply the transformer to flatten any tuple assignments
        transformer = FlattenTupleAssignments()
        transformed_ast = transformer.visit(parsed_ast)
        ast.fix_missing_locations(transformed_ast)

        return ast.unparse(transformed_ast)
    except SyntaxError:
        # Fallback logic
        normalized_lines = []
        for line in code_string.splitlines():
            if '#' in line:
                line = line.split('#')[0]
            line = line.rstrip()
            if line:
                normalized_lines.append(line)
        return "\n".join(normalized_lines)

# Gather all .m files dynamically from the fixed path
corrupted_files = list(M_DIR.glob("*.txt"))
print(M_DIR)


@pytest.mark.parametrize("corrupt_file", corrupted_files, ids=lambda f: f.stem)
def test_matlab_to_numpy(corrupt_file):
    # Locate the corresponding .py expected output file
    py_file = PY_DIR / f"{corrupt_file.stem}.py"

    # Ensure the expected output file exists before proceeding
    assert py_file.exists(), f"Missing expected output file: {py_file}"

    # Read the MATLAB input
    with open(corrupt_file, 'r', encoding='utf-8') as f:
        corrupt_content = f.read()

    # Read the expected Python output
    with open(py_file, 'r', encoding='utf-8') as f:
        expected_py_content = f.read()

    # Generate the actual Python output from your function
    actual_py_content = fix_code(corrupt_content)

    # Normalize both strings
    normalized_expected = normalize_python_code(expected_py_content)
    normalized_actual = normalize_python_code(actual_py_content)

    # Assert they are semantically identical
    assert normalized_actual == normalized_expected

