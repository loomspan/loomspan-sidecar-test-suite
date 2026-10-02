"""Verify actual provider calls exceed the previous limit and complete in Framework."""
import hashlib
import json
import os
from pathlib import Path

import pytest

capture=os.getenv('CAPTURE_DIRECTORY')
pytestmark=pytest.mark.skipif(not capture,reason='Set CAPTURE_DIRECTORY to actual snapshot runtime evidence')


@pytest.mark.parametrize('path',['java','sidecar'])
def test_supported_timeout_allows_calls_longer_than_sixty_seconds(path):
    directory=Path(capture)
    manifest=json.loads((directory/'manifest.json').read_text())
    assert manifest['framework']=='1.0.0-beta.8-SNAPSHOT'
    assert manifest['providerRequestTimeoutSeconds']==240
    events=json.loads((directory/'journal.json').read_text())
    requests={e['requestId']:e for e in events if e['event']=='model-request' and e.get('path')==path}
    long_responses=[e for e in events if e['event']=='model-response' and e.get('path')==path and
        e.get('status')==200 and e.get('requestId') in requests and
        60<(e['timeNs']-requests[e['requestId']]['timeNs'])/1e9<240]
    assert long_responses,'No independently recorded successful provider response beyond the old limit'
    # A proxy can finish after its caller disconnects. Also require a completed
    # model frame in the actual Framework trace, not just the upstream journal.
    durations=[]
    for trace in json.loads((directory/'trace-index.json').read_text()):
        if trace['path']!=path:continue
        raw=(directory/trace['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==trace['sha256']
        records=[json.loads(line) for line in raw.splitlines()]
        opened={r['frameId']:r for r in records if r['recordType']=='FRAME_OPENED'}
        for record in records:
            if (record['recordType']=='FRAME_CLOSED' and record.get('route','').endswith('-model')
                and record.get('metadata',{}).get('status')=='completed'):
                start=opened[record['frameId']]
                durations.append(float(record['timestamp'])-float(start['timestamp']))
    assert any(60<seconds<240 for seconds in durations),'Framework did not successfully consume a call beyond 60 seconds'
