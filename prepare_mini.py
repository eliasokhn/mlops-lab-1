from pathlib import Path
from PIL import Image
import shutil

DATA_DIR = Path("data/food11_processed_mini")

CATEGORIES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

for split in ["training", "validation", "evaluation"]:

    split_dir = DATA_DIR / split

    # Get original images before creating folders
    images = [
        p for p in split_dir.iterdir()
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ]

    counts = {label: 0 for label in CATEGORIES}

    # Create the 11 class folders
    for category in CATEGORIES.values():
        (split_dir / category).mkdir(exist_ok=True)

    for image_path in images:

        label = image_path.stem.split("_")[0]

        if label not in CATEGORIES:
            continue

        # Mini dataset: maximum 100 per category
        if counts[label] >= 100:
            continue

        category = CATEGORIES[label]
        destination = split_dir / category / image_path.name

        # Resize to 128x128
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize((128, 128))
            image.save(destination)

        counts[label] += 1

    print(f"{split}: {sum(counts.values())} images prepared")