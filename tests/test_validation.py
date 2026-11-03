from PIL import Image

from src.food11.clean_data import clean_dataset
from src.food11.data import CLASSES
from src.food11.validate_data import validate_dataset


def make_dataset(root):
    for s, split in enumerate(("training", "validation", "evaluation")):
        for c, category in enumerate(CLASSES):
            directory = root / split / category
            directory.mkdir(parents=True)
            Image.new("RGB", (128, 128), (s * 70, c * 20, 10)).save(directory / "image.png")


def test_contract_and_leakage(tmp_path, capsys):
    make_dataset(tmp_path)
    assert validate_dataset(tmp_path, min_per_class=1)
    source = tmp_path / "training/Bread/image.png"
    target = tmp_path / "evaluation/Bread/duplicate.png"
    target.write_bytes(source.read_bytes())
    assert not validate_dataset(tmp_path, min_per_class=1)
    assert "FAIL: no split leakage" in capsys.readouterr().out


def test_missing_dataset(tmp_path):
    assert not validate_dataset(tmp_path)


def test_cleanup_preserves_source(tmp_path):
    source, destination = tmp_path / "original", tmp_path / "clean"
    make_dataset(source)
    duplicate = source / "evaluation/Bread/duplicate.png"
    duplicate.write_bytes((source / "training/Bread/image.png").read_bytes())
    clean_dataset(source, destination)
    assert duplicate.exists()
    assert not (destination / "evaluation/Bread/duplicate.png").exists()
    assert validate_dataset(destination, min_per_class=1)


def test_bad_image_and_count(tmp_path, capsys):
    make_dataset(tmp_path)
    (tmp_path / "training/Bread/image.png").write_bytes(b"broken")
    assert not validate_dataset(tmp_path, min_per_class=2)
    report = capsys.readouterr().out
    assert "FAIL: image format" in report
    assert "FAIL: minimum counts" in report
