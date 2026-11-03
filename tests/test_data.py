import pytest
from PIL import Image

from src.food11.data import CLASSES, category_from_filename, resize_image


def test_categories():
    assert len(CLASSES) == 11
    assert category_from_filename("0_12.jpg") == "Bread"
    assert category_from_filename("10_3.jpg") == "Vegetable-Fruit"


@pytest.mark.parametrize("filename", ["-1_1.jpg", "11_1.jpg", "abc.jpg"])
def test_invalid_category(filename):
    with pytest.raises(ValueError):
        category_from_filename(filename)


def test_resize():
    image = Image.new("L", (512, 384))
    result = resize_image(image)
    assert result.size == (128, 128)
    assert result.mode == "RGB"
