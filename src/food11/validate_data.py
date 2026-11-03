import argparse
import hashlib
from pathlib import Path

from PIL import Image

try:
    from .data import CLASSES
except ImportError:
    from data import CLASSES


def validate_dataset(root: Path, min_per_class=50, tau=0.05):
    checks = dict.fromkeys(["class folders", "image format", "minimum counts",
                            "no split leakage", "class balance"], True)
    counts, seen = {}, {}
    for split in ("training", "validation", "evaluation"):
        folder = root / split
        folders = {p.name for p in folder.iterdir() if p.is_dir()} if folder.is_dir() else set()
        checks["class folders"] &= folders == set(CLASSES)
        counts[split] = {}
        for category in CLASSES:
            directory = folder / category
            files = [p for p in directory.iterdir() if p.is_file()] if directory.is_dir() else []
            counts[split][category] = len(files)
            checks["minimum counts"] &= len(files) >= min_per_class
            for path in files:
                try:
                    digest = hashlib.md5(path.read_bytes()).hexdigest()
                    if digest in seen and seen[digest] != split:
                        checks["no split leakage"] = False
                    seen.setdefault(digest, split)
                    with Image.open(path) as image:
                        image.load()
                        checks["image format"] &= image.mode == "RGB" and image.size == (128, 128)
                except (OSError, ValueError):
                    checks["image format"] = False
    train_total = sum(counts["training"].values())
    val_total = sum(counts["validation"].values())
    checks["class balance"] = bool(train_total and val_total) and all(
        abs(counts["training"][c] / train_total - counts["validation"][c] / val_total) <= tau
        for c in CLASSES
    )
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    return all(checks.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()
    if args.min_per_class < 1 or not 0 <= args.tau <= 1:
        parser.error("min-per-class must be positive; tau must be between 0 and 1")
    raise SystemExit(0 if validate_dataset(args.dataset, args.min_per_class, args.tau) else 1)
