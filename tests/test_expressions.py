import pytest

from qcref.expressions import evaluate
from qcref.models import Value


def v(value, uncertainty):
    return Value(value, "", "test", uncertainty, "")


NAMES = {"A": v(2.0, 0.1), "B": v(4.0, 0.2), "X": v(1.0, None)}


@pytest.mark.parametrize(
    "expression, value, uncertainty",
    [
        ("3", 3.0, 0.0),
        ("A * 10", 20.0, 1.0),
        ("1 / A", 0.5, 0.025),
        ("A + B", 6.0, (0.1**2 + 0.2**2) ** 0.5),
        ("-A", -2.0, 0.1),
        ("A * B", 8.0, 8.0 * (2 * 0.05**2) ** 0.5),
        ("A * X", 2.0, None),
    ],
)
def test_evaluate(expression, value, uncertainty):
    result = evaluate(expression, NAMES)
    assert result.value == pytest.approx(value)
    if uncertainty is None:
        assert result.uncertainty is None
    else:
        assert result.uncertainty == pytest.approx(uncertainty)


def test_decimal_arithmetic_avoids_float_noise():
    assert evaluate("A * 0.1", {"A": v(0.3, 0.0)}).value == 0.03


@pytest.mark.parametrize("expression", ["A ** 2", "f(A)", "A.real", "C", "'s'"])
def test_rejects_unsupported(expression):
    with pytest.raises(ValueError):
        evaluate(expression, NAMES)
