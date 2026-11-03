from src.food11.data import category_from_filename


def test_ci_failure_demonstration():
    # Intentional Lab 5 demonstration; fixed in the following PR commit.
    assert category_from_filename('0_12.jpg') == 'Egg'
