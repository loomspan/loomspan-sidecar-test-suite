"""Provider-free checks for source-preserving offer assembly and declared handoffs."""
import asyncio
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import author_workflow as author

spec = importlib.util.spec_from_file_location('offer_business', ROOT / 'apps/python/business.py')
business = importlib.util.module_from_spec(spec)
spec.loader.exec_module(business)


@pytest.mark.parametrize('reserved', [False, True])
def test_offers_preserve_source_terms_and_exact_persisted_quotes(tmp_path, monkeypatch, reserved):
    fixture = json.loads((ROOT / 'fixtures/business.json').read_bytes())
    for name in ['serviceResources', 'continuityOptions']:
        fixture[name].update(expiresAt='2030-01-02T11:15:00-08:00', reserved=reserved, revision='changed')
    fixture['continuityOptions']['replacement']['price'] = 7654321
    fixture['continuityOptions']['replacement']['supplierNote'] = 'Retain optional source detail'
    fixture['serviceResources']['expedited']['arrival'] = '2030-01-02T13:15:00-08:00/2030-01-02T15:45:00-08:00'
    fixture['serviceResources']['standard']['arrival'] = '2030-01-03T09:30:00-08:00/2030-01-03T11:00:00-08:00'
    fixture['serviceTerms']['rates'].update(sensor=12345, connector=6789, repairHourly=15432, expedited=32109)
    original = copy.deepcopy(fixture)
    async def record(case, kind):
        return {'data': copy.deepcopy(fixture[kind])}
    monkeypatch.setattr(business, 'record', record)
    monkeypatch.setattr(business, 'DB', str(tmp_path / 'business.db'))
    output = asyncio.run(business.leaf('quoteOptions', {'caseId': 'offer-test', 'assetId': 'NB-P240-017'},
                                      {'sub': 'maya', 'roles': ['ASSESS_EQUIPMENT']}))
    assert fixture == original
    with business.db() as db:
        persisted = {json.loads(row['body'])['option']: json.loads(row['body'])
                     for row in db.execute('select body from quotes')}
    for option, offer in output['offers'].items():
        source = fixture['serviceResources' if option in persisted else 'continuityOptions']
        assert offer['details'] == source[option]
        assert (offer['expiresAt'], offer['reserved'], offer['sourceId'], offer['sourceRevision']) == (
            source['expiresAt'], reserved, source['id'], 'changed')
        if option in persisted:
            assert offer['quote'] == persisted[option]
            assert offer['quote']['attendance'] == source[option]['arrival']
            quote = offer['quote']
            detail = quote['priceBreakdown']
            assert detail['rateSourceId'] == fixture['serviceTerms']['rates']['id']
            assert detail['rateSourceRevision'] == fixture['serviceTerms']['rates']['revision']
            assert detail['repairLabor'] == {'hours': 2, 'hourlyRate': 15432, 'maximum': 30864}
            assert detail['parts'] == [{'partId': 'S17-B', 'description': 'sensor', 'amount': 12345},
                                       {'partId': 'H17-B', 'description': 'connector kit', 'amount': 6789}]
            assert detail['attendancePremium'] == (32109 if option == 'expedited' else 0)
            assert quote['maxExposure'] == 30864 + 12345 + 6789 + detail['attendancePremium']
            assert quote['fullyCoveredScopeMaximum'] == detail['attendancePremium']
        else:
            assert 'quote' not in offer
    assert output['offers']['replacement']['details']['price'] == 7654321
    assert output['offers']['replacement']['details']['supplierNote'] == 'Retain optional source detail'
    assessment = dict(output, uncertainty=[], selectedOption='standard', acceptedRisk='',
                      nextDecision='', citations=[], equipmentAssessment={})
    assert business.save_assessment('original', json.dumps(assessment), {'sub': 'maya'}) == 'original-v1'
    altered = copy.deepcopy(assessment)
    altered['quotes'][0]['priceBreakdown']['parts'][0]['amount'] += 1
    with pytest.raises(business.HTTPException, match='model altered authoritative quote'):
        business.save_assessment('altered', json.dumps(altered), {'sub': 'maya'})


def test_all_assessors_receive_whole_offer_and_publish_its_terms():
    parent = yaml.safe_load((ROOT / 'config/skills/planResolution.yaml').read_bytes())
    for skill, (option, _) in author.FEASIBILITY.items():
        child = next(x for x in parent['allowed_skills'] if x['name'] == skill)
        bindings = child['input_bindings']
        assert bindings['/context/offer'] == {'from': 'child_result', 'skill': 'quoteOptions',
                                              'path': '/offers/' + option}
        assert not any(k in bindings for k in ['/context/quotes', '/context/offerExpiresAt',
                                              '/context/offerReserved', '/context/offerSourceId'])
        manifest = yaml.safe_load((ROOT / ('config/skills/' + skill + '.yaml')).read_bytes())
        assert manifest['input_schema'] == author.CONTRACTS['feasibilityInput']
        for published, key in [('offerExpiresAt', 'expiresAt'), ('offerReserved', 'reserved'),
                               ('offerSourceId', 'sourceId')]:
            assert manifest['output_bindings']['/' + published]['path'] == '/context/offer/' + key
    comparison = next(x for x in parent['allowed_skills'] if x['name'] == 'compareOptions')
    assert comparison['input_bindings']['/context/offers']['path'] == '/offers'
    schema = author.CONTRACTS['compareOptions']['properties']['context']['properties']['offers']
    for record in schema['properties'].values():
        assert record == author.CONTRACTS['feasibilityInput']['properties']['context']['properties']['offer']
