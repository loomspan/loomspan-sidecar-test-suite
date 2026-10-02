"""Versioned source records; excludes evaluator commentary from retrieved passages."""
import json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=(ROOT/'docs/equipment-service-source-pack.md').read_text(encoding='utf-8')
manual=[{'id':m.group(1),'revision':'2.0' if m.group(1).startswith('MAN') else '1','issuer':'Aster Equipment','text':m.group(2)} for m in re.finditer(r'\*\*((?:MAN-\d\.\d|SB-\d))[^*]*\*\* (.+)',source)]
terms=[{'id':m.group(1),'revision':'1','text':m.group(2).strip()} for m in re.finditer(r'\| ((?:W|S)-\d) \| (.+?) \|',source)]
for passage in manual:
    passage['applicability']={'manufacturer':'Aster Equipment','model':'P240','hardwareRevision':'B'}
    if passage['id'].startswith('SB'):
        passage['applicability']['serialRangeInclusive']=['AP24B-0400','AP24B-0799']
data={
 'assetContext':{'id':'ASSET-017','revision':'1','issuer':'Northbank asset administration','assetId':'NB-P240-017','serial':'AP24B-0517','manufacturer':'Aster Equipment','model':'P240','hardwareRevision':'B','commissioned':'2025-02-10','owner':'Northbank Fulfillment','site':{'id':'SITE-WEST','revision':'1','siteId':'NB-WEST','timezone':'America/Los_Angeles','access':'08:00-18:00; later access must be arranged with Luis Romero'},'approvalContext':{'id':'AUTH-NB','revision':'1','currency':'USD','monetaryUnit':'cents','luisMaximumCustomerExposure':100000,'mayaMayCommit':False,'largerCommitments':'Require separately verified approval from Priya Shah; the current service-request workflow does not implement procurement approval.','permissionBoundary':'Informational routing only. Verified caller permissions, site grants, spending ceiling and explicit approval are enforced independently by the application.'},'contacts':[{'id':'CONTACT-MAYA','revision':'1','name':'Maya Chen','responsibility':'Operator and incident reporter','email':'maya.chen@northbank.example'},{'id':'CONTACT-LUIS','revision':'1','name':'Luis Romero','responsibility':'Maintenance manager and access contact','hours':'08:00-18:00','email':'luis.romero@northbank.example'},{'id':'CONTACT-PRIYA','revision':'1','name':'Priya Shah','responsibility':'Procurement approval contact','hours':'09:00-17:00','email':'priya.shah@northbank.example'},{'id':'CONTACT-BEACON','revision':'1','name':'Erin Cole','responsibility':'Dispatch; service-request queue is authoritative for status','email':'dispatch@beacon-service.example'},{'id':'CONTACT-WARRANTY','revision':'1','responsibility':'Aster warranty review for disputed findings','email':'warranty@aster-equipment.example'}]},
 'serviceHistory':[
  {'id':'WO-0820','revision':'1','date':'2026-08-20','author':'Jo Ellis, authorized technician','observation':'Replaced S17-B after E17; suspected sensor fault; 20-minute test without recurrence'},
  {'id':'NOTE-0916','revision':'1','date':'2026-09-16','author':'Maya Chen','observation':'E17 after 42 minutes; restart temporarily effective; linked to WO-0820'},
  {'id':'MAINT-0710','revision':'1','date':'2026-07-10','author':'Jo Ellis','observation':'Scheduled inspection complete, no open exceptions'},
  {'id':'MAINT-0928','revision':'1','date':'2026-09-28','author':'Maya Chen','observation':'Operator condition/cleaning complete, no visible window obstruction'}],
 'referenceEvidence':manual,
 'serviceTerms':{'clauses':terms,'certificate':{'id':'WC-017','revision':'1','start':'2025-02-10','endExclusive':'2027-02-10'},'agreement':{'id':'SA-NB-2026','revision':'1','start':'2026-01-01','endExclusive':'2027-01-01','diagnosisIncluded':True,'travelIncluded':True},'rates':{'id':'RATE-09','revision':'1','currency':'USD','diagnosis':25000,'travel':10000,'repairHourly':15000,'sensor':12000,'connector':6000,'expedited':30000}},
 'entitlements':{'id':'FINDINGS-017','revision':'1','findings':[],'maintenanceRecordAvailable':True},
 'serviceResources':{'id':'RESOURCES-017','revision':'1','observedAt':'2026-09-29T09:05:00-07:00','expiresAt':'2026-09-29T11:00:00-07:00','parts':[{'id':'S17-B','quantity':2,'revision':'B'},{'id':'H17-B','quantity':1,'revision':'B'}],'expedited':{'id':'SLOT-EXP-017','arrival':'2026-09-29T14:00:00-07:00/2026-09-29T16:00:00-07:00','technician':'Jo Ellis','qualification':'P240-B','workEstimateHours':[2,4]},'standard':{'id':'SLOT-STD-017','arrival':'2026-09-30T10:00:00-07:00/2026-09-30T12:00:00-07:00'},'reserved':False},
 'continuityOptions':{'id':'CONTINUITY-017','revision':'1','expiresAt':'2026-09-29T11:00:00-07:00','loaner':{'id':'LOAN-017','model':'P240-B','capacityPerMinute':20,'price':240000,'currency':'USD','arrival':'2026-09-29T20:00:00-07:00/2026-09-29T22:00:00-07:00','durationDays':3},'replacement':{'id':'REPLACE-017','price':1250000,'leadBusinessDays':10,'installationQuoted':False},'reserved':False},
 'clock':{'now':'2026-09-29T09:05:00-07:00'}}
data['serviceTerms']['rates']['monetaryUnit']='cents'
data['continuityOptions']['monetaryUnit']='cents'
data['continuityOptions']['currency']='USD'
data['continuityOptions']['loaner']['packageIncludes']=['delivery and setup window','three-day use','return']
data['continuityOptions']['loaner']['compatible']=True
data['continuityOptions']['replacement']['currency']='USD'
data['continuityOptions']['replacement']['model']='P240'
data['continuityOptions']['replacement']['hardwareRevision']='B'
data['continuityOptions']['replacement']['compatible']=True
data['serviceTerms']['certificate']['serial']='AP24B-0517'
data['serviceTerms']['agreement']['assetId']='NB-P240-017'
data['serviceTerms']['agreement']['siteId']='NB-WEST'
(ROOT/'fixtures/business.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
case={'assetId':'NB-P240-017','context':{'incident':'E17 stops after 35-50 minutes warm-up, restarts after cooling; permitted cleaning did not resolve three recurrences. No smoke, unusual odor or damaged guard reported.','productionStart':'2026-09-30T06:00:00-07:00','recoverableDelayHours':2,'lostMorningShift':'threatens shipment','minimumCapacityPerMinute':18,'restorationRiskPreference':'unspecified','siteAccess':'08:00-18:00; later access must be arranged with Luis','businessNow':'2026-09-29T09:05:00-07:00'}}
(ROOT/'fixtures/base-case.json').write_text(json.dumps(case,indent=2),encoding='utf-8')
