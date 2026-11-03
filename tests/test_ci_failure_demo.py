from src.food11.data import category_from_filename


def test_ci_failure_demonstration():
    # Corrected after the protected PR demonstrated a failing required check.
    assert category_from_filename('0_12.jpg') == 'Bread'
