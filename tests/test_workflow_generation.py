"""Regeneration must preserve the revised deployed decision contracts."""
import yaml
import author_workflow
from conftest import ROOT


def test_regeneration_preserves_business_fixes(monkeypatch, tmp_path):
    monkeypatch.setattr(author_workflow, 'ROOT', tmp_path)
    author_workflow.main()
    for name in ['assessEquipment', 'compareOptions', 'planResolution', 'resolveEquipment']:
        file = 'config/skills/' + name + '.yaml'
        assert yaml.safe_load((tmp_path / file).read_text()) == yaml.safe_load((ROOT / file).read_text())
