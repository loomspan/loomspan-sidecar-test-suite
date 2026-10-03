"""Capture labels must describe the running JARs, including local snapshot builds."""
import environment as target_env
import json
import pathlib
import subprocess

ROOT=pathlib.Path(__file__).resolve().parents[1]

def baseline():
    file=ROOT/'.runtime/build-baseline.json'
    if not file.exists():
        return {'framework':'1.0.0-beta.7','frameworkCommit':'0778065ef5bafc9c8ea979093e5e0e48d7e1e687',
                'sidecar':'1.0.0-beta.2','sidecarCommit':'da3bb8f8ae6087955f9b3a6bd02b9706d3b582e7'}
    result=json.loads(file.read_text())
    for path,jar in [('java','/app/app.jar'),('sidecar','/app/loomspan-sidecar.jar')]:
        actual=subprocess.check_output(target_env.execute(path,'sha256sum',jar),text=True).split()[0]
        if actual!=result['artifacts'][path]['sha256']:
            raise RuntimeError('Running '+path+' JAR differs from recorded build baseline; rebuild/deploy consistently before capture')
        for variable,field,default in [('LOOMSPAN_CONNECTIONS_MODEL_REQUESTTIMEOUT','providerRequestTimeoutSeconds','60s'),
                                       ('LOOMSPAN_SESSION_MISSIONTIMEOUT','missionTimeoutSeconds','600s')]:
            observed=subprocess.run(target_env.execute(path,'printenv',variable),capture_output=True,text=True)
            if observed.returncode not in [0,1]:raise RuntimeError('Unable to verify running timeout configuration')
            if (observed.stdout.strip() or default)!=str(result[field])+'s':
                raise RuntimeError('Running '+path+' timeout differs from recorded build baseline')
    result['runtimeIdentity'] = target_env.runtime_identity()
    return result
