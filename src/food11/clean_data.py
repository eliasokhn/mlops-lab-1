"""Create a separate processed dataset without cross-split duplicate content."""
import argparse
import hashlib
import shutil
from pathlib import Path

try:
    from .data import CLASSES
    from .validate_data import validate_dataset
except ImportError:
    from validate_data import validate_dataset

    from data import CLASSES


def clean_dataset(source: Path, destination: Path):
    source, destination = source.resolve(), destination.resolve()
    if destination == source or source in destination.parents:
        raise ValueError("Destination must be separate from source")
    # Refuse overwriting any existing dataset.
    destination.mkdir(parents=True, exist_ok=False)
    seen, skipped = {}, []
    for split in ("training", "validation", "evaluation"):
        for category in CLASSES:
            target = destination / split / category
            target.mkdir(parents=True)
            for path in sorted((source / split / category).iterdir()):
                if not path.is_file():
                    continue
                digest = hashlib.md5(path.read_bytes()).hexdigest()
                if digest in seen and seen[digest] != split:
                    skipped.append(path.relative_to(source).as_posix())
                    continue
                seen.setdefault(digest, split)
                shutil.copy2(path, target / path.name)
    print(f"Skipped {len(skipped)} later-split duplicates; original data preserved.")
    (destination / "excluded-duplicates.txt").write_text("\n".join(skipped) + "\n")
    return validate_dataset(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if clean_dataset(args.source, args.destination) else 1)
