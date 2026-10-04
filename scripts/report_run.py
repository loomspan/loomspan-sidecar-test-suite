"""Re-report retained live evidence offline into a NEW directory; preserve original artifacts."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from run_suite import summary


def regenerate(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    report = copy.deepcopy(json.loads(source.read_bytes()))
    if report.get('mode') not in {'live', 'evaluate', 'capture'}:
        raise ValueError('Only live/evaluate/capture suite reports are supported')
    protected = [source.parent] + [Path(s['capture']).resolve() for s in report['stages']]
    if any(output.is_relative_to(p) for p in protected):
        raise ValueError('Output must be outside the original suite and captures')
    output.mkdir(parents=True, exist_ok=False)
    for stage in report['stages']:
        stage.pop('diagnostics', None)
        stage.pop('diagnosticError', None)
    report['diagnosticReanalysis'] = {'sourceReport': str(source),
        'sourceReportSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'note': 'Offline diagnostic view of retained results, not a new execution, acceptance or semantic review.'}
    summary(output, report)
    return output / 'summary.md'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='New output directory')
    args = parser.parse_args()
    print(regenerate(args.report, args.output))
