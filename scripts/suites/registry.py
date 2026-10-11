"""Explicit suite catalog. Importing it never starts services or enables providers."""
from dataclasses import dataclass
from .equipment_service import scenarios


@dataclass(frozen=True)
class Suite:
    name: str
    scenarios: object
    modes: tuple
    entry_skill: str
    endpoint: str
    database: str
    tables: tuple
    reference_loader: object
    source_files: tuple
    scope: str
    mock_runner: object = None
    live_runner: object = None

    @property
    def skill_directory(self):
        return 'config/skills/' + self.name


def equipment_reference(root):
    from replay_reference import load_reference
    return load_reference(root)


EQUIPMENT = Suite(
    'equipment-service', scenarios, ('mock', 'evaluate', 'live', 'capture'),
    'resolveEquipment', '/assessments', 'equipment.db', ('assessments', 'quotes', 'requests'),
    equipment_reference,
    ('fixtures/base-case.json', 'fixtures/business.json', 'fixtures/server.py',
     'scripts/suites/equipment_service/scenarios.py', 'scripts/run_suite.py'),
    'Assessment scenarios only; service-request regression is separate')
def typesafe_mock(args, parser, suite, core):
    from .typesafe_ai.runner import run
    return run(args, parser, suite, core)


from .typesafe_ai import scenarios as typesafe_scenarios
def typesafe_live(args, parser, suite, core):
    from .typesafe_ai.live import run
    return run(args, parser, suite, core)


TYPESAFE = Suite('typesafe-ai', typesafe_scenarios, ('mock', 'live', 'capture', 'evaluate'), 'tsTriageFixed',
    '/suites/typesafe-ai', '', (), typesafe_scenarios.load,
    ('fixtures/typesafe-ai/cases.json', 'fixtures/typesafe.py'),
    'System One protocol and bounded live judgments', typesafe_mock, typesafe_live)
SUITES = {EQUIPMENT.name: EQUIPMENT, TYPESAFE.name: TYPESAFE}


def select(names):
    names = names or [EQUIPMENT.name]
    if 'all' in names:
        if names != ['all']:
            raise ValueError('--suite all cannot be combined with named suites')
        return list(SUITES.values())
    return [SUITES[name] for name in dict.fromkeys(names)]
