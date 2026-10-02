"""Offline authorization scaffolding cannot invent receipts or bypass stage exhaustion."""
import asyncio,copy,importlib,json
import pytest
from fastapi import HTTPException

@pytest.fixture
def server(monkeypatch,tmp_path):
    monkeypatch.setenv('FIXTURE_DATA',str(tmp_path));monkeypatch.setenv('CONTROL_KEY','control')
    server=importlib.import_module('fixtures.server');monkeypatch.setattr(server,'DATA',tmp_path)
    monkeypatch.setattr(server,'lock',asyncio.Lock());monkeypatch.setattr(server,'cases',{'case':{'mode':'replay','steps':[{'contains':['case']}],'used':[]}})
    return server

def test_extension_cannot_reset_or_skip_existing_stages(server):
    async def run():
        before=copy.deepcopy(server.cases['case'])
        with pytest.raises(HTTPException):await server.extend('case',{'expectedUsed':[0],'steps':[{'contains':['case']}]},'control')
        assert server.cases['case']==before
        server.cases['case']['used']=[0]
        with pytest.raises(HTTPException) as error:await server.extend('case',{'expectedUsed':[0],'steps':[{'live':True}]},'control')
        assert error.value.status_code==400
        with pytest.raises(HTTPException) as error:await server.extend('case',{'expectedUsed':[0],'steps':[{'contains':['case']}]},'wrong')
        assert error.value.status_code==403
        await server.extend('case',{'expectedUsed':[0],'steps':[{'contains':['case'],'after':[0]}]},'control')
        assert server.cases['case']['steps'][0]==before['steps'][0] and server.cases['case']['used']==[0]
        assert len(server.cases['case']['steps'])==2
    asyncio.run(run())

def test_final_copies_real_completed_receipt_exactly(server):
    receipt={'requestId':'real-id','approval':{'cap':78000,'approved':True},'status':'PENDING_DISPATCH'}
    task={'taskId':'delegate','skillName':'createServiceRequest','result':json.dumps(receipt)}
    body={'messages':[{'role':'system','content':'--- COMPLETED TASK EVIDENCE ---\n'+json.dumps([task])}]}
    response=server.completed_task_response(body,{'taskId':'delegate','skillName':'createServiceRequest'})
    assert response['model']=='meta/muse-spark-1.3-contributor'
    content=json.loads(response['choices'][0]['message']['content']);assert json.loads(content['finalResponse'])==receipt
    assert content['stepAction']=='FINAL_RESPONSE'
    for tasks in [[],[task,task],[{**task,'result':'malformed'}]]:
        changed={'messages':[{'role':'system','content':'--- COMPLETED TASK EVIDENCE ---\n'+json.dumps(tasks)}]}
        with pytest.raises(HTTPException) as error:server.completed_task_response(changed,{'taskId':'delegate','skillName':'createServiceRequest'})
        assert error.value.status_code==409
