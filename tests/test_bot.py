import pytest
from services.numerology_service import calculate_life_path_number

@pytest.mark.parametrize("birth_date, expected", [
    ("12.05.1990", 9),  # 1+2+0+5+1+9+9+0 = 27 → 2+7 = 9 ✅
    ("01.01.2000", 4),  # 0+1+0+1+2+0+0+0 = 4 ✅ (исправлено!)
    ("15.07.1985", 9),  # 1+5+0+7+1+9+8+5 = 36 → 3+6 = 9 ✅
])
def test_calculate_life_path_number(birth_date, expected):
    assert calculate_life_path_number(birth_date) == expected
