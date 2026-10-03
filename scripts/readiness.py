import environment as target_env
import time, httpx
def ready(timeout=120):
    pending={'java':target_env.url(18081, '/health', '127.0.0.1'),'python':target_env.url(18082, '/health', '127.0.0.1'),'fixtures':target_env.url(18090, '/health', '127.0.0.1'),'keycloak':target_env.url(18080, '/realms/equipment/.well-known/openid-configuration', '127.0.0.1'),'sidecar':target_env.url(19091, '/actuator/health/readiness', '127.0.0.1')}
    deadline=time.monotonic()+timeout
    with httpx.Client(timeout=2,trust_env=False) as c:
        while pending and time.monotonic()<deadline:
            for name,url in list(pending.items()):
                try:
                    if c.get(url).status_code==200: del pending[name]
                except httpx.HTTPError: pass
            if pending: time.sleep(1)
    if pending: raise RuntimeError('Services not ready: '+', '.join(pending))
    discovery=httpx.get(target_env.url(18080,'/realms/equipment/.well-known/openid-configuration'),trust_env=False,timeout=5)
    discovery.raise_for_status()
    if discovery.json()['issuer'] != target_env.issuer():
        raise RuntimeError('Keycloak issuer differs from the selected runtime target')
if __name__=='__main__':ready();print('All five services ready.')
