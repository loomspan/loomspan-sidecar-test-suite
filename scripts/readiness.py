import time, httpx
def ready(timeout=120):
    pending={'java':'http://127.0.0.1:18081/health','python':'http://127.0.0.1:18082/health','fixtures':'http://127.0.0.1:18090/health','keycloak':'http://127.0.0.1:18080/realms/equipment/.well-known/openid-configuration','sidecar':'http://127.0.0.1:19091/actuator/health/readiness'}
    deadline=time.monotonic()+timeout
    with httpx.Client(timeout=2,trust_env=False) as c:
        while pending and time.monotonic()<deadline:
            for name,url in list(pending.items()):
                try:
                    if c.get(url).status_code==200: del pending[name]
                except httpx.HTTPError: pass
            if pending: time.sleep(1)
    if pending: raise RuntimeError('Services not ready: '+', '.join(pending))
if __name__=='__main__':ready();print('All five services ready.')
