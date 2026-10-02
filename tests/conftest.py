import json, pathlib, sys, time
import httpx, pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from login import login
from capture import collect
from readiness import ready
from finalize_evidence import finalize
from baseline import baseline
class Harness(dict):
    def __repr__(self): return '<Harness: credentials redacted>'
@pytest.fixture(scope='session')
def harness():
    ready()
    build=baseline()
    secrets=json.loads((ROOT/'.runtime/secrets.json').read_text())
    tokens={user:login(user) for user in ['maya','luis']}
    out=ROOT/'evidence'/('checks-'+time.strftime('%Y%m%d-%H%M%S'));out.mkdir(parents=True)
    with httpx.Client(timeout=300,trust_env=False) as client:
        h=Harness(client=client,secrets=secrets,tokens=tokens,out=out,cases=[])
        yield h
        collect(client,out,h['cases'],secrets,tokens.values())
        (out/'manifest.json').write_text(json.dumps({**build,'scope':'Compatibility and deterministic skill checks; NOT first-delivery acceptance','cases':h['cases']},indent=2))
        finalize(out)
@pytest.fixture(params=[('java',18081),('sidecar',18082)])
def target(request):return request.param[0],f'http://127.0.0.1:{request.param[1]}'
