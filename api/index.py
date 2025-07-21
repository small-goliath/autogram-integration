import logging
import logging.config
import os
from fastapi import FastAPI
from api.router import api_router

# 로그 디렉토리 생성
if not os.path.exists('logs'):
    os.makedirs('logs')

# 로깅 설정 파일 로드 (프로젝트 루트 기준)
logging.config.fileConfig('core/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(api_router, prefix="/api")

