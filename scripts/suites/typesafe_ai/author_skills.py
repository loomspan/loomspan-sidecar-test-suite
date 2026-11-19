"""Maintain customer-support judgment declarations, independently of response fixtures."""
from pathlib import Path
import copy
import json
import textwrap
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
    def represent_str(self, value):
        style = '|' if '\n' in value else None
        return self.represent_scalar('tag:yaml.org,2002:str', value, style=style)

    def ignore_aliases(self, data):
        # Framework manifests require expanded schemas rather than YAML anchors.
        return True


ManifestDumper.add_representer(str, ManifestDumper.represent_str)


def main():
    directory = ROOT / 'config/skills/typesafe-ai'
    directory.mkdir(parents=True, exist_ok=True)
    def save(doc):
        manifest = yaml.dump(doc, Dumper=ManifestDumper, sort_keys=False)
        (directory / (doc['name'] + '.yaml')).write_text(manifest, encoding='utf-8')

    def leaf(name, questions, properties=None, *, state='.context', definitions='', **extra):
        properties = properties or {'context': CONTEXT}
        # Question literals are JSON, a subset of JSLT. Dynamic leaves supply JSLT directly.
        if isinstance(questions, dict):
            questions = json.dumps(questions, indent=2, ensure_ascii=False)
        question_block = textwrap.indent(questions, '  ').lstrip()
        expression = definitions + (
            '{\n  "model": "jev-1.13.0",\n'
            f'  "state": {state},\n'
            f'  "questions": {question_block}\n'
            '}\n'
        )
        doc = dict(name=name, description='Evaluate support-contact judgments; no ticket routing or customer action.',
                   executor='typesafe', input_schema={'type': 'object', 'properties': properties,
                    'required': list(properties), 'additionalProperties': False},
                   input_transform={'language': 'jslt', 'expression': expression}, **extra)
        save(doc)
        return doc
    fixed = leaf('tsTriageFixed', QUESTIONS, config={'max_attempts': 1})
    leaf('tsTriageEvidence', {
        'impactEvidence': {'type': 'noul',
            'instructions': 'What do the current observations establish about application functionality across the people and functions described? Answer yes if they identify normal operation, partial impairment, or total loss. Judge functional evidence independently of the tone or subject of the complaint.',
            'criteria': {
                'true': 'An explicit current statement that every function works establishes normal operation, even during an angry complaint about another issue. Explicit loss of all access establishes total loss. For partial impairment, a current failure and a current working function or unaffected group suffice, including across different sites. No complete inventory is needed.',
                'false': 'The functional extent is unknown: the rest is untested after a failure, or equally credible reports contradict each other about the same scope and time. Urgency or detailed billing or delivery facts without a functional observation, a vague symptom, or a resolved ticket without a current check cannot establish the category.'}},
        'impact': {'type': 'score',
            'instructions': 'Rate the current reported loss of application functionality. Ignore resolved past incidents and emotional urgency.',
            'criteria': ['All application functions work normally',
                         'Some application functions fail while others work',
                         'All application functionality is blocked']}})
    for name, key in [('Choice', 'department'), ('Noul', 'repeat'), ('Score', 'impact')]:
        leaf('tsTriage'+name, {key: QUESTIONS[key]})
    dynamic = {
        key: json.dumps(question['instructions']) for key, question in QUESTIONS.items()
    }
    leaf('tsTriageDynamic', """{
  "department": {"type": "choice", "instructions": %s, "criteria": .candidates},
  "repeat": {"type": "noul", "instructions": %s, "criteria": .noulCriteria},
  "impact": {"type": "score", "instructions": %s, "criteria": .parameters.levels}
}""" % (dynamic['department'], dynamic['repeat'], dynamic['impact']),
         {'context': CONTEXT, 'candidates': CONTEXT, 'noulCriteria': CONTEXT, 'parameters': CONTEXT})
    structured = leaf('tsTriageStructured', """{
  "department": {"type": "choice", "criteria": .candidates, "instructions": {
    "question": "Which team should review " + scalar(.context.message, "message") + "?",
    "policy": .policy
  }},
  "repeat": {"type": "noul", "instructions": ["Check contact history.", .context.history[0]],
             "criteria": {"true": null}},
  "impact": {"type": "score", "criteria": .parameters.levels}
}""", {'context': CONTEXT, 'policy': CONTEXT, 'candidates': CONTEXT, 'parameters': CONTEXT},
        state='''{
    "contact": .context, "slash": .context."a/b", "tilde": .context."a~b",
    "literal": "${/input/notResolved}",
    "note": "Repeat=" + scalar(.context.repeat, "repeat") + "; count=" + scalar(.context.count, "count")
  }''', definitions='''def scalar(value, field)
  if (is-string($value) or is-number($value) or is-boolean($value)) string($value)
  else error("Expected text, number or boolean for " + $field)

''')
    save(dict(name='tsTriageStructuredForward', description='Forward the structured contact judgments.',
              model='coordination', thinking_level='medium', planning_mode=True, max_steps=1,
              prompt='Have tsTriageStructured assess the supplied contact.',
              input_schema=structured['input_schema'], allowed_skills=[dict(name='tsTriageStructured',
                  required=True, max_tasks=1, input_bindings={
                      '/' + key: {'from': 'input', 'path': '/' + key}
                      for key in structured['input_schema']['required']})],
              output_from={'skill': 'tsTriageStructured'}))
    leaf('tsTriageRouter', QUESTIONS)
    for suffix in ('Retry', 'Timeout'):
        leaf('tsTriage' + suffix, QUESTIONS)
    leaf('tsTriageStructuredLive', """{
  "department": {"type": "choice", "instructions": {
    "question": "Which support team should review this contact?", "policy": .policy
  }, "criteria": .candidates},
  "repeat": {"type": "noul", "instructions": [
    "Does the contact describe a previous support attempt?", "Consider only the supplied contact and its history."
  ], "criteria": {"true": "Previous support attempt is described", "false": "No previous attempt is described"}},
  "impact": {"type": "score", "instructions": {
    "question": "Rate the reported loss of functionality.",
    "guidance": "Do not infer detailed symptoms absent from the contact."
  }, "criteria": .parameters.levels}
}""", {'context': CONTEXT, 'policy': CONTEXT, 'candidates': CONTEXT, 'parameters': CONTEXT})
    leaf('tsTriageRestricted', QUESTIONS, rbac_roles=['TRIAGE_ADMIN'])
    leaf('tsTriageMissingPath', QUESTIONS, state='.context.absent')
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
            parent['output_bindings'] = {target: {'from': 'child_result', 'skill': 'tsTriageFixed', 'path': '/answers' + source}
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
            parent['output_bindings'] = {'/' + key: {'from': 'child_result', 'skill': 'tsTriageEvidence', 'path': '/answers/' + key}
                                         for key in ('impactEvidence', 'impact')}
        else:
            parent['output_from'] = {'skill': 'tsTriageEvidence'}
        save(parent)


if __name__ == '__main__':
    main()
