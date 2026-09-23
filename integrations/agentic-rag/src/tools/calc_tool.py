import ast
import operator

# Allowed operators and functions for safe evaluation
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_ALLOWED_FUNCS = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "sum": sum,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op = _ALLOWED_BINOPS.get(type(node.op))
        if not op:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _ALLOWED_UNARYOPS.get(type(node.op))
        if not op:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise ValueError("Unsupported function")
        args = [_eval_node(a) for a in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)
    if isinstance(node, ast.Tuple) or isinstance(node, ast.List):
        return [_eval_node(e) for e in node.elts]
    raise ValueError(f"Unsupported expression: {type(node).__name__}")


def calculate(expression: str) -> dict:
    """
    Safe arithmetic evaluator. Supports + - * / // % ** and a small
    allowlist of functions (abs, min, max, round, sum).
    """
    try:
        tree = ast.parse(expression, mode="eval")
        value = _eval_node(tree)
        return {
            "tool": "calculate",
            "ok": True,
            "result": {"expression": expression, "value": value},
            "summary": f"{expression} = {value}",
            "error": None,
        }
    except Exception as e:
        return {
            "tool": "calculate",
            "ok": False,
            "result": None,
            "summary": f"Calculation failed: {e}",
            "error": str(e),
        }


if __name__ == "__main__":
    import json

    for expr in ["2 + 2", "(45 - 12) * 3 / 4", "round(2.718, 2)", "__import__('os').system('ls')"]:
        print(json.dumps(calculate(expr), indent=2))