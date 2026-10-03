"""Select refreshable business fixtures; static fault fixtures retain their original source."""
import json
import os
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / 'fixtures/replay/active-business.json'


def business_fixture(selected=None):
    selected = selected or os.getenv('LOOMSPAN_BUSINESS_FIXTURE')
    pointer = None
    if not selected and POINTER.exists():
        pointer = json.loads(POINTER.read_bytes())
        selected = pointer['fixture']
    file = (ROOT / (selected or 'fixtures/replay/business-reviewed-v1.json')).resolve()
    if not file.is_relative_to((ROOT / 'fixtures/replay').resolve()):
        raise ValueError('Business fixture must be under fixtures/replay')
    if pointer and hashlib.sha256(file.read_bytes()).hexdigest() != pointer['fixtureSha256']:
        raise ValueError('Active business fixture hash mismatch')
    return file


def approval_file(file=None):
    file = file or business_fixture()
    return file.with_name(file.stem + '-approval.json')
