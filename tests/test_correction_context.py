"""Detect prefix/excerpt loss even when a plausible corrected response succeeds."""
import json
import pytest
from review_correction_context import decoded_candidate,exact_large_candidate


@pytest.mark.parametrize('kind',['schema','step'])
def test_complete_large_unicode_candidate_required(kind):
    original='x'*8192+'🚀middle'*1500+'尾}}'
    def request(value):
        return {'messages':[{'role':'assistant','content':value}]} if kind=='schema' else {
            'messages':[{'role':'user','content':'Rejected assistant response (JSON string): '+json.dumps(value)+'\nFailure diagnostic: syntax'}]}
    assert decoded_candidate(request(original),kind)==original
    assert exact_large_candidate(request(original),original,kind)
    assert not exact_large_candidate(request(original[:8192]),original,kind)
    assert not exact_large_candidate(request(original[:4096]+'[omitted]'+original[-4096:]),original,kind)
    assert not exact_large_candidate(request(original.replace('尾','changed')),original,kind)


@pytest.mark.parametrize('kind',['schema','step'])
def test_ambiguous_candidate_rejected(kind):
    message={'role':'assistant','content':'candidate'} if kind=='schema' else {
        'role':'user','content':'Rejected assistant response (JSON string): '+json.dumps('candidate')}
    with pytest.raises(ValueError):decoded_candidate({'messages':[message,message]},kind)
