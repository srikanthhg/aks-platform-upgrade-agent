from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from api.models import DecisionRequest, StartWorkflowRequest, WorkflowResponse
from api.security import current_identity, require_api_key
from services.workflow_service import WorkflowConflictError, WorkflowNotFoundError, WorkflowService
from tools.audit import read_audit
from tools.markdown import get_report

router = APIRouter()
service = WorkflowService()

@router.get('/me')
def me(identity: dict = Depends(current_identity)):
    return {'actor':identity['actor'],'roles':identity.get('roles',[])}

@router.get('/audit')
def audit(limit:int=Query(default=50,ge=1,le=200), actor: str = Depends(require_api_key)):
    return {'items':read_audit(limit)}

@router.get('/workflows/{thread_id}/reports/{stage}')
def report(thread_id:str,stage:str,actor:str=Depends(require_api_key)):
    if stage not in {'pre-upgrade-report','post-upgrade-report'}: raise HTTPException(400,'Invalid report stage.')
    item=get_report(thread_id,stage)
    if not item: raise HTTPException(404,'Report not found.')
    return Response(content=item['content'],media_type='text/markdown',headers={'Content-Disposition':f'attachment; filename="{item["filename"]}"'})

@router.post('/workflows', response_model=WorkflowResponse, status_code=201)
def start(request: StartWorkflowRequest, actor: str = Depends(require_api_key)):
    try: return service.start(request.model_dump(), actor)
    except WorkflowConflictError as exc: raise HTTPException(409, str(exc)) from exc
    except Exception as exc: raise HTTPException(500, str(exc)) from exc

@router.get('/workflows/{thread_id}', response_model=WorkflowResponse)
def get(thread_id: str, actor: str = Depends(require_api_key)):
    try: return service.get(thread_id)
    except WorkflowNotFoundError as exc: raise HTTPException(404, 'Workflow not found.') from exc

@router.post('/workflows/{thread_id}/approve', response_model=WorkflowResponse)
def approve(thread_id: str, request: DecisionRequest, actor: str = Depends(require_api_key)):
    try: return service.resume(thread_id, True, actor, request.comment)
    except WorkflowNotFoundError as exc: raise HTTPException(404, 'Workflow not found.') from exc
    except WorkflowConflictError as exc: raise HTTPException(409, str(exc)) from exc

@router.post('/workflows/{thread_id}/reject', response_model=WorkflowResponse)
def reject(thread_id: str, request: DecisionRequest, actor: str = Depends(require_api_key)):
    try: return service.resume(thread_id, False, actor, request.comment)
    except WorkflowNotFoundError as exc: raise HTTPException(404, 'Workflow not found.') from exc
    except WorkflowConflictError as exc: raise HTTPException(409, str(exc)) from exc
