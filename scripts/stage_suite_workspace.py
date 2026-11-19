"""Stage the suite sources in a fresh suite workspace."""
import argparse
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]


def stage(destination):
    destination.mkdir(parents=True, exist_ok=False)
    for name in ('apps', 'deploy', 'fixtures', 'scripts', 'config'):
        shutil.copytree(ROOT / name, destination / name,
                        ignore=shutil.ignore_patterns('target', '__pycache__'))
    for name in ('compose.yaml', 'compose.runtime.yaml', 'compose.offline.yaml',
                 '.dockerignore', 'requirements.lock'):
        shutil.copyfile(ROOT / name, destination / name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    stage(parser.parse_args().destination.resolve())
