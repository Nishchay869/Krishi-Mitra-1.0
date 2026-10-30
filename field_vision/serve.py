"""Start only with locally trained artifacts and a passing independent test report."""
from contextlib import asynccontextmanager
from dataclasses import asdict
import hmac
import json
import logging
import os
from pathlib import Path
import uuid

from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from starlette.concurrency import run_in_threadpool
from .common import sha256
from .inference import Engine, Policy

logger = logging.getLogger('field_vision')


@asynccontextmanager
async def lifespan(app):
    token = os.environ.get('VISION_API_KEY', '')
    if len(token) < 24:
        raise RuntimeError('Set VISION_API_KEY to a strong random secret of at least 24 characters')
    report = json.loads(Path(os.environ['VISION_REPORT']).read_text())
    if not report.get('release_passed') or report.get('split') != 'test':
        raise RuntimeError('Independent field-test release criteria have not passed')
    weights, gate = os.environ['VISION_WEIGHTS'], Path(os.environ['VISION_GATE'])
    hashes = {'weights':sha256(weights),'leaf_gate':sha256(gate/'leaf_gate.pt'),'ood':sha256(gate/'ood.npz')}
    if hashes != report['artifacts']:
        raise RuntimeError('Model artifacts differ from the evaluated release')
    app.state.engine = Engine(weights, gate, Policy(**report['policy']), os.environ.get('VISION_DEVICE','cpu'))
    app.state.token = token
    yield


app = FastAPI(title='Field lesion analysis', lifespan=lifespan)


@app.get('/health')
def health():
    return {'status':'ready'}


@app.post('/predict')
async def predict(file: UploadFile = File(...), authorization: str = Header(default='')):
    if not hmac.compare_digest(authorization, 'Bearer '+app.state.token):
        raise HTTPException(401, 'Unauthorized')
    raw = await file.read(app.state.engine.policy.max_bytes+1)
    await file.close()
    if len(raw) > app.state.engine.policy.max_bytes:
        raise HTTPException(413, 'Image is too large')
    request_id = str(uuid.uuid4())
    try:
        result = await run_in_threadpool(app.state.engine.predict, raw)
    except Exception:
        logger.exception('inference_failed request_id=%s',request_id)
        raise HTTPException(503, 'Analysis unavailable; try again later')
    logger.info('request_id=%s status=%s reason=%s',request_id,result['status'],result.get('reason',''))
    return {**result, 'request_id':request_id}
