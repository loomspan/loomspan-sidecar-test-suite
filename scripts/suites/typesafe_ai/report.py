"""Report Framework calls separately from TypeSafe transport and response usage."""
import json


def request_usage(journal, mode):
    attempt_event = 'native-request' if mode == 'mock' else 'native-live-attempt'
    attempts = [event['requestId'] for event in journal if event['event'] == attempt_event]
    responses = {event['requestId']: event.get('response') for event in journal
                 if event['event'] == 'native-response'}
    counts = {'typeSafeRequestAttempts': len(attempts)}
    for key, field in [('input_tokens', 'typeSafeInputTokens'), ('output_tokens', 'typeSafeOutputTokens')]:
        total = 0
        for request_id in attempts:
            body = responses.get(request_id)
            usage = body.get('usage') if isinstance(body, dict) else None
            value = usage.get(key) if isinstance(usage, dict) else None
            if type(value) is not int or value < 0:
                total = None
                break
            total += value
        counts[field] = total
    return counts


def usage_table(report, bundle):
    fields = ('modelCalls', 'typeSafeRequestAttempts', 'typeSafeInputTokens', 'typeSafeOutputTokens')
    totals = dict.fromkeys(fields, 0)
    lines = [
        '| Scenario | Path | Checks | Framework model calls | TypeSafe request attempts | '
        'TypeSafe-reported input tokens | TypeSafe-reported output tokens | Reported cost | Trace seconds |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|',
    ]

    def row(cells):
        return '| ' + ' | '.join('—' if value is None else str(value) for value in cells) + ' |'

    for case in report['cases']:
        usage = case['usage']
        key = f"{case['scenario']}/{case['path']}/journal.json"
        if key in bundle.files:
            usage.update(request_usage(json.loads(bundle.files[key]), report['mode']))
        checks = case['checks']
        counts = [usage.get(field) for field in fields]
        lines.append(row([case['scenario'], case['path'], f'{sum(checks.values())}/{len(checks)}',
                          *counts, usage.get('reportedCost'), usage.get('traceSeconds')]))
        for field, value in zip(fields, counts):
            if value is None:
                totals[field] = None
            elif totals[field] is not None:
                totals[field] += value

    report['usageTotals'] = totals
    lines.append(row(['**Total**', '', '', *totals.values(), '', '']))
    if report['mode'] == 'mock':
        lines.extend(['', 'TypeSafe attempts target the fixture. Token counts come from replayed responses.'])
    lines.extend(['', 'A dash means the value is unavailable. A token total requires a valid count for every attempt.'])
    return lines
