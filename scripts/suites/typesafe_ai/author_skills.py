"""Maintain customer-support judgment declarations, independently of response fixtures."""
from pathlib import Path
import copy
import yaml

ROOT = Path(__file__).resolve().parents[3]
QUESTIONS = {
    'department': {'type': 'choice', 'instructions': 'Which support team should review this contact?',
                   'criteria': {'billing': 'Charges, invoices and refunds', 'technical': 'Product failures',
                                'delivery': 'Shipment and delivery problems', 'other': 'None of the listed teams'}},
    'repeat': {'type': 'noul', 'instructions': 'Does the customer describe a previous support attempt?'},
    'impact': {'type': 'score', 'instructions': 'Rate the reported loss of functionality.',
               'criteria': ['No loss of functionality', 'Some functions impaired', 'Core operation blocked']},
}
CONTEXT = {'type': 'object', 'additionalProperties': True}


class ManifestDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        # Framework manifests require expanded schemas rather than YAML anchors.
        return True


def main():
    directory = ROOT / 'config/skills/typesafe-ai'
    directory.mkdir(parents=True, exist_ok=True)
    def save(doc):
        (directory / (doc['name'] + '.yaml')).write_text(yaml.dump(doc, Dumper=ManifestDumper, sort_keys=False), encoding='utf-8')
    def leaf(name, questions, properties=None, state='${/input/context}', model='typesafeTriage', **extra):
        properties = properties or {'context': CONTEXT}
        doc = dict(name=name, description='Evaluate support-contact judgments; no ticket routing or customer action.',
                   model=model, input_schema={'type': 'object', 'properties': copy.deepcopy(properties),
                    'required': list(properties), 'additionalProperties': False},
                   typesafe={'state': state, 'questions': copy.deepcopy(questions)}, **extra)
        save(doc)
        return doc
    fixed = leaf('tsTriageFixed', QUESTIONS)
    leaf('tsTriageEvidence', {
        'impactEvidence': {'type': 'noul',
            'instructions': 'Does the supplied contact establish the current extent of application functionality well enough to assess functional impact?',
            'criteria': {
                'true': 'Concrete, mutually consistent current observations identify what works or fails, including an explicit statement that everything works normally or that all functionality is blocked.',
                'false': 'Only vague symptoms or urgency, no application-functionality observations, or unresolved conflicting current reports. Do not infer scope from emotion or assume that missing information means normal operation.'}},
        'impact': {'type': 'score',
            'instructions': 'Rate the current reported loss of application functionality. Ignore resolved past incidents and emotional urgency.',
            'criteria': ['All application functions work normally',
                         'Some application functions fail while others work',
                         'All application functionality is blocked']}})
    for name, key in [('Choice', 'department'), ('Noul', 'repeat'), ('Score', 'impact')]:
        leaf('tsTriage'+name, {key: QUESTIONS[key]})
    dynamic = copy.deepcopy(QUESTIONS)
    dynamic['department']['criteria'] = '${/input/candidates}'
    dynamic['repeat']['criteria'] = '${/input/noulCriteria}'
    dynamic['impact']['criteria'] = '${/input/parameters/levels}'
    leaf('tsTriageDynamic', dynamic, {'context': CONTEXT, 'candidates': CONTEXT,
         'noulCriteria': CONTEXT, 'parameters': CONTEXT})
    leaf('tsTriageStructured', {
        'department': {'type': 'choice', 'instructions': {'question': 'Which team should review ${/input/context/message}?',
                       'policy': '${/input/policy}'}, 'criteria': '${/input/candidates}'},
        'repeat': {'type': 'noul', 'instructions': ['Check contact history.', '${/input/context/history/0}'],
                   'criteria': {'true': None}},
        'impact': {'type': 'score', 'criteria': '${/input/parameters/levels}'}},
        {'context': CONTEXT, 'policy': CONTEXT, 'candidates': CONTEXT, 'parameters': CONTEXT},
        state={'contact': '${/input/context}', 'slash': '${/input/context/a~1b}',
               'tilde': '${/input/context/a~0b}', 'literal': '$${/input/notResolved}',
               'note': 'Repeat=${/input/context/repeat}; count=${/input/context/count}'})
    for suffix, model in [('Router', 'typesafeTriageRouter'), ('Retry', 'typesafeTriageRetry'),
                          ('Timeout', 'typesafeTriageTimeout')]:
        leaf('tsTriage'+suffix, QUESTIONS, model=model)
    leaf('tsTriageStructuredLive', {
        'department': {'type': 'choice', 'instructions': {'question': 'Which support team should review this contact?',
                       'policy': '${/input/policy}'}, 'criteria': '${/input/candidates}'},
        'repeat': {'type': 'noul', 'instructions': ['Does the contact describe a previous support attempt?',
                   'Consider only the supplied contact and its history.'],
                   'criteria': {'true': 'Previous support attempt is described', 'false': 'No previous attempt is described'}},
        'impact': {'type': 'score', 'instructions': {'question': 'Rate the reported loss of functionality.',
                   'guidance': 'Do not infer detailed symptoms absent from the contact.'},
                   'criteria': '${/input/parameters/levels}'}},
        {'context': CONTEXT, 'policy': CONTEXT, 'candidates': CONTEXT, 'parameters': CONTEXT})
    leaf('tsTriageRestricted', QUESTIONS, rbac_roles=['TRIAGE_ADMIN'])
    leaf('tsTriageMissingPath', QUESTIONS, state='${/input/context/absent}')
    for name, assembly in [('tsTriageForward', False), ('tsTriageSummary', True)]:
        parent = dict(name=name, description='Coordinate contact triage and preserve its judgments.',
            model='coordination', thinking_level='medium', planning_mode=True, max_steps=1,
            prompt='Have tsTriageFixed assess the supplied contact. Do not route tickets or take customer actions.',
            input_schema=copy.deepcopy(fixed['input_schema']), allowed_skills=[dict(name='tsTriageFixed',
                required=True, max_tasks=1, input_bindings={'/context': {'from': 'input', 'path': '/context'}})])
        if assembly:
            parent['output_schema'] = {'type': 'object', 'properties': {
                'department': {'type': 'string', 'enum': list(QUESTIONS['department']['criteria'])},
                'repeatProbability': {'type': 'number'}, 'impact': {'type': 'number'}},
                'required': ['department', 'repeatProbability', 'impact'], 'additionalProperties': False}
            parent['output_bindings'] = {target: {'from': 'child_result', 'skill': 'tsTriageFixed', 'path': source}
                for target, source in [('/department', '/department/choice'),
                                       ('/repeatProbability', '/repeat/noul'), ('/impact', '/impact/score')]}
        else:
            parent['output_from'] = {'skill': 'tsTriageFixed'}
        save(parent)

    for name, assembly in [('tsTriageEvidenceForward', False), ('tsTriageEvidenceSummary', True)]:
        parent = dict(name=name, description='Demonstrate native evidence handoff to an application impact policy.',
            model='coordination', thinking_level='medium', planning_mode=True, max_steps=1,
            prompt='Have tsTriageEvidence assess the supplied contact. Preserve its judgments for the application policy.',
            input_schema=copy.deepcopy(fixed['input_schema']), allowed_skills=[dict(name='tsTriageEvidence',
                required=True, max_tasks=1, input_bindings={'/context': {'from': 'input', 'path': '/context'}})])
        if assembly:
            parent['output_schema'] = {'type': 'object', 'properties': {
                'impactEvidence': copy.deepcopy(CONTEXT), 'impact': copy.deepcopy(CONTEXT)},
                'required': ['impactEvidence', 'impact'], 'additionalProperties': False}
            parent['output_bindings'] = {'/' + key: {'from': 'child_result', 'skill': 'tsTriageEvidence', 'path': '/' + key}
                                         for key in ('impactEvidence', 'impact')}
        else:
            parent['output_from'] = {'skill': 'tsTriageEvidence'}
        save(parent)


if __name__ == '__main__':
    main()
