"""Deterministic application operations. Runner expectations never import this module."""
import datetime as dt, hashlib, json, os, sqlite3, uuid
import httpx
from fastapi import HTTPException
DB='/data/equipment.db'
def db():
    c=sqlite3.connect(DB,timeout=30); c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS assessments(version TEXT PRIMARY KEY, owner TEXT, asset TEXT, body TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS requests(owner TEXT, key TEXT, content TEXT, receipt TEXT, PRIMARY KEY(owner,key))')
    c.execute('CREATE TABLE IF NOT EXISTS quotes(id TEXT PRIMARY KEY, body TEXT)')
    return c
def scoped(who,asset):
    if who['sub'] not in ['maya','luis'] or asset not in ['NB-P240-017','NB-P240-018']: raise HTTPException(403,'site scope denied')
def role(who,name):
    if name not in who.get('roles',[]): raise HTTPException(403,'permission denied')
async def record(case,kind):
    async with httpx.AsyncClient(timeout=240) as client:
        r=await client.get(os.environ['FIXTURES']+'/records/'+case+'/'+kind); r.raise_for_status(); return r.json()
async def leaf(name,body,who):
    role(who,'ASSESS_EQUIPMENT'); scoped(who,body['assetId'])
    case=body['caseId']; asset=body['assetId']
    if name=='quoteOptions':
        # Re-read authoritative inputs: a model-supplied amount never establishes a quote.
        terms=(await record(case,'serviceTerms'))['data']; resources=(await record(case,'serviceResources'))['data']
        entitlement=await leaf('entitlements',body,who)
        rates=terms['rates']; repair=2*rates['repairHourly']+rates['sensor']+rates['connector']
        quotes=[]
        for option,premium in [('expedited',rates['expedited']),('standard',0)]:
            quotes.append({'quoteId':case+'-'+option+'-v1','option':option,'currency':'USD','maxExposure':repair+premium,'fullyCoveredScopeMaximum':premium,'coverage':'PENDING','attendance':resources[option]['arrival'],'scope':{'repairHours':2,'parts':['S17-B','H17-B'],'onlyIfJustifiedByTechnician':True},'expiresAt':resources['expiresAt'],'reservation':False,'restorationGuaranteed':False})
        with db() as c:
            for quote in quotes: c.execute('INSERT OR IGNORE INTO quotes VALUES(?,?)',(quote['quoteId'],json.dumps(quote,sort_keys=True)))
        return {'caseId':case,'assetId':asset,'quotes':quotes,'entitlement':entitlement}
    result=await record(case,name); result['assetId']=asset
    if name=='assetContext' and result['data']['assetId']!=asset:
        raise HTTPException(404,'registered asset context unavailable')
    if name=='entitlements':
        # Routine findings are authoritative fixture records, never context supplied by the model.
        terms=(await record(case,'serviceTerms'))['data']; now=dt.datetime.fromisoformat((await record(case,'clock'))['data']['now']).date()
        cert=terms['certificate']; in_period=dt.date.fromisoformat(cert['start'])<=now<dt.date.fromisoformat(cert['endExclusive'])
        findings=result['data']['findings']; covered=[]
        for finding in findings:
            if in_period and finding.get('authorizedTechnician') and finding.get('confirmedManufacturingDefect') and not finding.get('disputed'): covered.extend(finding['items'])
        result['determination']={'status':'PARTIAL_OR_COVERED' if covered else 'PENDING' if in_period else 'OUTSIDE_PERIOD','coveredItems':covered,'diagnosisIncluded':True,'travelIncluded':True,'premiumCovered':False}
    return result
def save_assessment(execution,result,who):
    parsed=json.loads(result); scoped(who,parsed['assetId'])
    required=['uncertainty','quotes','selectedOption','acceptedRisk','nextDecision','citations','equipmentAssessment']
    if any(k not in parsed for k in required): raise HTTPException(502,'incomplete assessment')
    if parsed['selectedOption'] not in ['expedited','standard','loaner','replacement','defer','undecided']:
        raise HTTPException(502,'selectedOption must be an option name, not a quote ID')
    version=execution+'-v1'
    with db() as c:
        expected={parsed['caseId']+'-'+option+'-v1' for option in ['expedited','standard']}
        if len(parsed['quotes'])!=2 or {q.get('quoteId') for q in parsed['quotes']}!=expected:
            raise HTTPException(502,'missing, duplicate or foreign-case quote')
        for quote in parsed['quotes']:
            row=c.execute('SELECT body FROM quotes WHERE id=?',(quote.get('quoteId'),)).fetchone()
            if not row or json.loads(row['body'])!=quote: raise HTTPException(502,'model altered authoritative quote')
        if not parsed['quotes']: raise HTTPException(502,'missing quotes')
        c.execute('INSERT OR IGNORE INTO assessments VALUES(?,?,?,?)',(version,who['sub'],parsed['assetId'],json.dumps(parsed,sort_keys=True)))
    return version
async def create(approval,who):
    role(who,'REQUEST_SERVICE')
    if who['sub']!='luis': raise HTTPException(403,'no spending grant')
    required={'assessmentVersion','option','quoteId','attendance','scope','cap','idempotencyKey','approved'}
    if not required.issubset(approval) or approval['approved'] is not True: raise HTTPException(400,'explicit complete approval required')
    content=json.dumps(approval,sort_keys=True,separators=(',',':')); owner=who['iss']+'|'+who['sub']
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        old=c.execute('SELECT * FROM requests WHERE owner=? AND key=?',(owner,approval['idempotencyKey'])).fetchone()
        if old:
            if old['content']!=content: raise HTTPException(409,'idempotency content conflict')
            return json.loads(old['receipt'])
        assessment=c.execute('SELECT * FROM assessments WHERE version=?',(approval['assessmentVersion'],)).fetchone()
        if not assessment: raise HTTPException(404,'assessment not found')
        scoped(who,assessment['asset']); value=json.loads(assessment['body'])
        quote=next((q for q in value['quotes'] if q['quoteId']==approval['quoteId'] and q['option']==approval['option']),None)
        if not quote: raise HTTPException(409,'quote not in assessment')
        if any(approval[k]!=quote[k] for k in ['attendance','scope']) or approval['cap']!=quote['maxExposure'] or approval['cap']>100000: raise HTTPException(409,'approved terms do not match quote or ceiling')
        clock=(await record(value['caseId'],'clock'))['data']['now']
        if dt.datetime.fromisoformat(clock)>=dt.datetime.fromisoformat(quote['expiresAt']): raise HTTPException(409,'requote required')
        receipt={'requestId':str(uuid.uuid4()),'status':'PENDING_DISPATCH','assetId':assessment['asset'],'caseId':value['caseId'],'approval':approval,'approver':{'issuer':who['iss'],'subject':who['sub']},'quote':quote,'evidence':value['citations'],'createdAt':clock}
        c.execute('INSERT INTO requests VALUES(?,?,?,?)',(owner,approval['idempotencyKey'],content,json.dumps(receipt,sort_keys=True)))
    return receipt
def recover(key,who):
    role(who,'REQUEST_SERVICE')
    with db() as c: row=c.execute('SELECT receipt FROM requests WHERE owner=? AND key=?',(who['iss']+'|'+who['sub'],key)).fetchone()
    if not row: raise HTTPException(404)
    return json.loads(row['receipt'])
