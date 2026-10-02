"""Publication must reject damaged captured quotes, even if structurally valid."""
import copy
import json
import pytest
from fastapi import HTTPException
from apps.python import business
from conftest import ROOT


@pytest.mark.parametrize('damage',['extra','missing','duplicate','dollars','foreign'])
def test_captured_quote_mutations_cannot_publish(monkeypatch,tmp_path,damage):
    monkeypatch.setattr(business,'DB',str(tmp_path/'business.db'))
    source=json.loads((ROOT/'fixtures/replay/quote-contract-diagnostic-v1.json').read_text())
    value=json.loads(source['samples']['sidecar']['response']['choices'][0]['message']['content'])
    with business.db() as c:
        for quote in value['quotes']:
            c.execute('INSERT INTO quotes VALUES(?,?)',(quote['quoteId'],json.dumps(quote)))
    if damage=='extra':value['quotes'].append({'option':'loaner','price':240000})
    if damage=='missing':value['quotes'].pop()
    if damage=='duplicate':value['quotes'][1]=copy.deepcopy(value['quotes'][0])
    if damage=='dollars':value['quotes'][0]['maxExposure']=780
    if damage=='foreign':value['caseId']='another-case'
    with pytest.raises(HTTPException):
        business.save_assessment('diagnostic',json.dumps(value),{'sub':'maya'})
    with business.db() as c:assert c.execute('SELECT COUNT(*) FROM assessments').fetchone()[0]==0
