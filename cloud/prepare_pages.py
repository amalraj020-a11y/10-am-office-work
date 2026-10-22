"""Publish only website assets; preserve each shop's distinct path."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '_pages'


def ignored(directory, names):
    return [name for name in names if name in {'.git', '.DS_Store', '.env', 'node_modules'}
            or (Path(directory) / name).is_symlink()]


if __name__ == '__main__':
    if DEST.exists():
        raise RuntimeError('Use a clean checkout; the output directory already exists')
    DEST.mkdir()
    # Preserve the existing root demo while giving every business a stable subpath.
    current = ROOT / 'websites/sikkim-momo-gr-cafe'
    if current.is_dir():
        shutil.copytree(current, DEST, dirs_exist_ok=True, ignore=ignored)
    for folder in ('websites', 'sites'):
        if (ROOT / folder).is_dir():
            shutil.copytree(ROOT / folder, DEST / folder, ignore=ignored)
    shots = ROOT / 'work/screenshots'
    if shots.is_dir():
        target = DEST / 'work/screenshots'
        target.mkdir(parents=True)
        for source in shots.iterdir():
            if source.is_file() and not source.is_symlink() and source.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
                shutil.copy2(source, target / source.name)
    (DEST / '.nojekyll').touch()
