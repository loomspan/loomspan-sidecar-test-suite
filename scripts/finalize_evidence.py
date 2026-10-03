"""Collect bounded diagnostics and independent SQLite records; never copy secrets."""
import environment as target_env
import hashlib, json, os, pathlib, sqlite3, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def finalize(directory):
    out=pathlib.Path(directory).resolve();secrets=list(json.loads((ROOT/'.runtime/secrets.json').read_text()).values())
    secrets += [v for k,v in os.environ.items() if ('API_KEY' in k or 'TOKEN' in k) and len(v)>15]
    def redact(text):
        for secret in secrets:text=text.replace(secret,'[REDACTED]')
        return text
    log=subprocess.check_output(target_env.compose()+['logs','--no-color'],cwd=ROOT,text=True,encoding='utf-8',errors='replace')
    (out/'containers.log').write_text(redact(log),encoding='utf-8')
    identities={}
    services={item['Service']: item for item in target_env.services()}
    images={item['ContainerName']:item['ID'] for item in json.loads(subprocess.check_output(target_env.compose()+['images','--format','json'],text=True))}
    for service in ['java','python','sidecar','fixtures','keycloak']:
        name=services[service]['Name']
        image=images[name]
        identities[service]={'container':name,'imageId':image}
        if service in ['java','sidecar']:
            jar='/app/app.jar' if service=='java' else '/app/loomspan-sidecar.jar'
            identities[service]['runningJarSha256']=subprocess.check_output(target_env.execute(service,'sha256sum',jar),text=True).split()[0]
    (out/'running-identities.json').write_text(json.dumps(identities,indent=2))
    # Preserve the authored public configuration with the run, not credentials.
    configuration=out/'configuration'
    for source in [ROOT/'compose.yaml',ROOT/'compose.snapshot.yaml',*(ROOT/'config').rglob('*.yaml')]:
        if not source.exists():continue
        target=configuration/source.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(redact(source.read_text(encoding='utf-8')),encoding='utf-8')
    for path in ['java','python']:
        db=ROOT/'.runtime'/path/'equipment.db'
        if not db.exists():continue
        with sqlite3.connect(f'file:{db.as_posix()}?mode=ro',uri=True) as c:
            c.row_factory=sqlite3.Row
            records={table:[dict(row) for row in c.execute('SELECT * FROM '+table)] for table in ['assessments','quotes','requests']}
        (out/(path+'-business-records.json')).write_text(json.dumps(records,indent=2),encoding='utf-8')
    files={}
    for p in sorted(out.rglob('*')):
        if not p.is_file() or p.name=='checksums.json':continue
        raw=p.read_bytes()
        if any(s.encode() in raw for s in secrets):raise RuntimeError('Secret detected in evidence file '+p.name)
        files[p.relative_to(out).as_posix()]=hashlib.sha256(raw).hexdigest()
    (out/'checksums.json').write_text(json.dumps(files,indent=2))
    print('Collected logs, running artifact identities, independent business records and evidence checksums.')
if __name__=='__main__':finalize(sys.argv[1])
