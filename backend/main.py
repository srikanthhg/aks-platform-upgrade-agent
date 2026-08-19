from __future__ import annotations
import shutil
from contextlib import asynccontextmanager
from typing import AsyncIterator
import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from config import get_settings
from tools.logger import logger
settings=get_settings()
@asynccontextmanager
async def lifespan(app:FastAPI)->AsyncIterator[None]:
    logger.info('AKS Upgrade Agent API starting in %s mode',settings.app_environment); yield; logger.info('AKS Upgrade Agent API stopping')
app=FastAPI(title='AKS Upgrade Agent API',version='4.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=False,allow_methods=['GET','POST','OPTIONS'],allow_headers=['Authorization','Content-Type','X-API-Key'])
app.include_router(router,prefix='/api/v1',tags=['workflows'])
@app.get('/health')
def health(): return {'status':'healthy'}
@app.get('/ready')
def ready():
    try:
        with psycopg.connect(settings.database_url,connect_timeout=5) as c: c.execute('SELECT 1').fetchone()
    except Exception as exc: raise HTTPException(503,f'PostgreSQL is not ready: {exc}') from exc
    return {'status':'ready'}
@app.get('/diagnostics')
def diagnostics(): return {'environment':settings.app_environment,'auth_mode':settings.auth_mode,'allow_real_upgrades':settings.allow_real_upgrades,'default_dry_run':settings.default_dry_run,'database':'postgresql','az_available':shutil.which('az') is not None,'kubectl_available':shutil.which('kubectl') is not None,'kubelogin_available':shutil.which('kubelogin') is not None,'multi_replica_supported':True}
