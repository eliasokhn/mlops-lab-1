from PIL import Image

CLASSES = ["Bread", "Dairy product", "Dessert", "Egg", "Fried food", "Meat",
           "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit"]


def category_from_filename(filename: str) -> str:
    label = filename.split("_", 1)[0]
    if not label.isdigit() or not 0 <= int(label) < len(CLASSES):
        raise ValueError(f"Invalid Food-11 filename: {filename}")
    return CLASSES[int(label)]


def resize_image(img: Image.Image, size: int = 128) -> Image.Image:
    return img.convert("RGB").resize((size, size))
