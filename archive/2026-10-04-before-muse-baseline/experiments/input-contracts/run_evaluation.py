"""Evaluate the closed-source skill candidate through the standard suite runner.

Normal skills and approved replay fixtures remain unchanged. Candidate skills are
copied into the standard per-run overlay and retained with their provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_suite

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args, suite_args = parser.parse_known_args()
    out = args.evidence_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'run-overlay.json').exists():
        parser.error('Use a fresh evidence directory; this one already contains a run overlay.')
    candidates = Path(__file__).resolve().parent / 'closed-sources/skills'
    normal = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT / 'config/skills').glob('*.yaml')}
    original = run_suite.make_overlay
    def candidate_overlay(directory, paths, model, reasoning):
        overlay = original(directory, paths, model, reasoning)
        saved = out / 'skills'; saved.mkdir(exist_ok=True)
        for source in candidates.glob('*.yaml'):
            text = source.read_text(encoding='utf-8')
            text = re.sub(r'^thinking_level:.*\n', '' if reasoning is None else 'thinking_level: '+reasoning+'\n', text, flags=re.M)
            (directory / 'skills' / source.name).write_text(text, encoding='utf-8')
            (saved / source.name).write_text(text, encoding='utf-8')
        (out / 'run-overlay.json').write_text(json.dumps({
            'directory': str(directory), 'overlay': str(overlay),
            'candidate': str(candidates), 'normalSkillHashes': normal}, indent=2))
        return overlay
    run_suite.make_overlay = candidate_overlay
    sys.argv = ['run_suite.py', 'evaluate', *suite_args]
    try:
        return run_suite.main()
    finally:
        run_suite.make_overlay = original
        assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest
                   for p, digest in normal.items()), 'Normal skills changed during candidate evaluation'
        (out / 'normal-skills-unchanged.json').write_text(json.dumps(normal, indent=2))

if __name__ == '__main__':
    raise SystemExit(main())
