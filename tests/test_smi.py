import math

import pytest

from flood_mismatch.smi import compute_smi


def test_perfect_alignment_has_zero_smi():
    result = compute_smi([10, 20, 30], [1, 2, 3])
    assert math.isclose(result.smi, 0.0)


def test_complete_two_unit_mismatch_is_one():
    result = compute_smi([100, 0], [0, 100])
    assert math.isclose(result.smi, 1.0)


def test_negative_values_rejected():
    with pytest.raises(ValueError):
        compute_smi([1, -1], [1, 1])
