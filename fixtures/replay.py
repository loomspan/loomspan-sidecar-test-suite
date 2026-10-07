"""Strict semantic request matching for the frozen reference assessment responses."""
import json
import re


def structured(value):
    """Ignore JSON object ordering/encoding, including Framework's JSON result strings."""
    if isinstance(value, dict):
        return {k: structured(v) for k, v in value.items()}
    if isinstance(value, list):
        return [structured(v) for v in value]
    if isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        try:
            return structured(json.loads(value))
        except ValueError:
            pass
    return value


def request_contract(body):
    messages = body['messages']
    users = [m['content'] for m in messages if m['role'] == 'user']
    systems = [m['content'] for m in messages if m['role'] == 'system']
    if len(users) != 1 or len(systems) != 1 or len(messages) != 2:
        raise ValueError('Expected one mission message and one system message')
    user, system = users[0], systems[0]
    skill = re.search(r"Fulfill the mission for skill '([^']+)'", user)
    if not skill:
        raise ValueError('Missing mission skill')
    mission = json.JSONDecoder().raw_decode(user.split('Canonical mission input:\n', 1)[1].lstrip())[0]
    task = None
    if '--- ASSIGNED TASK ---\n' in system:
        task = system.split('--- ASSIGNED TASK ---\n', 1)[1].split('\n--- ', 1)[0].strip()
    completed = []
    if '--- COMPLETED TASK EVIDENCE ---\n' in system:
        block = system.split('--- COMPLETED TASK EVIDENCE ---\n', 1)[1].lstrip()
        completed = structured(json.JSONDecoder().raw_decode(block[block.index('['):])[0])
        # Parallel completion order has no meaning; task identity and contents do.
        completed.sort(key=lambda t: t['taskId'])
        if len({t['taskId'] for t in completed}) != len(completed):
            raise ValueError('Duplicate completed task evidence')
    return {'skill': skill[1], 'model': body['model'], 'reasoning': body.get('reasoning_effort'),
            'mission': structured(mission), 'assignedTask': task, 'completedEvidence': completed}


def request_matches(body, expected):
    try:
        return request_contract(body) == expected
    except (KeyError, IndexError, TypeError, ValueError):
        return False
