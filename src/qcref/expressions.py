"""Evaluate arithmetic expressions over named Values.

Supports numbers, names, unary +/-, and binary + - * /. Values are computed with
`Decimal` to avoid float round-off, and uncertainties are propagated to first
order assuming uncorrelated inputs. Number literals are exact.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from math import hypot

from .models import Value


@dataclass(frozen=True)
class Result:
    """Outcome of evaluating an expression.

    Attributes:
        value: Computed value.
        uncertainty: Propagated standard uncertainty, or None if any input's
            uncertainty is unknown.
        inputs: Named Values referenced by the expression, in evaluation order
            and repeated if a name occurs more than once.
    """

    value: float
    uncertainty: float | None
    inputs: list[Value]


def evaluate(expression: str, names: Mapping[str, Value]) -> Result:
    """Evaluate an arithmetic expression over named Values.

    Args:
        expression: Expression built from number literals, keys of ``names``,
            unary + and -, and binary + - * /.
        names: Values the expression may reference by name.

    Returns:
        The value, its propagated uncertainty, and the Values referenced.

    Raises:
        SyntaxError: If the expression cannot be parsed.
        ValueError: If the expression references an unknown name or uses
            unsupported syntax.
    """
    inputs: list[Value] = []

    def ev(node: ast.AST) -> tuple[Decimal, float | None]:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value)), 0.0
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise ValueError(f"Unknown name {node.id!r} in {expression!r}.")
            named = names[node.id]
            inputs.append(named)
            return Decimal(repr(float(named))), named.uncertainty
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            v, u = ev(node.operand)
            return (-v if isinstance(node.op, ast.USub) else v), u
        if isinstance(node, ast.BinOp):
            a, ua = ev(node.left)
            b, ub = ev(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                value = a + b if isinstance(node.op, ast.Add) else a - b
                return value, _combine(ua, ub, lambda x, y: hypot(x, y))
            fa, fb = float(a), float(b)
            if isinstance(node.op, ast.Mult):
                return a * b, _combine(ua, ub, lambda x, y: hypot(fb * x, fa * y))
            if isinstance(node.op, ast.Div):
                return a / b, _combine(
                    ua, ub, lambda x, y: hypot(x / fb, fa * y / fb**2)
                )
        raise ValueError(f"Unsupported syntax in {expression!r}: {ast.dump(node)}")

    value, uncertainty = ev(ast.parse(expression.strip(), mode="eval").body)
    return Result(float(value), uncertainty, inputs)


def _combine(
    ua: float | None, ub: float | None, rule: Callable[[float, float], float]
) -> float | None:
    return None if ua is None or ub is None else rule(ua, ub)
