"""Capture labels must describe the artifacts in the running containers."""
import environment as target_env
import json
import pathlib
import subprocess

ROOT=pathlib.Path(__file__).resolve().parents[1]

def baseline():
    file=ROOT/'.runtime/build-baseline.json'
    if not file.exists():
        raise RuntimeError('Record the current packages with scripts/record_build.py before checking runtime identity')
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
    sdk = result['artifacts']['pythonSdk']
    for service in ('python', 'fixtures'):
        observed = subprocess.run(target_env.execute(service, 'sha256sum', '--', '/sdk/' + sdk['filename']),
                                  capture_output=True, text=True)
        if observed.returncode or observed.stdout.split()[:1] != [sdk['sha256']]:
            raise RuntimeError(f'Running {service} SDK wheel differs from recorded build baseline. Rebuild before capture.')
    result['runtimeIdentity'] = target_env.runtime_identity()
    return result
