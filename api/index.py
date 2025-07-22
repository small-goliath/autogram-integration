import logging
import logging.config
import os
from fastapi import FastAPI
from backend.router import api_router

# Vercel 환경에서는 파일 시스템이 읽기 전용이므로 파일 로그를 사용하지 않음
if not os.getenv('VERCEL'):
    # 로그 디렉토리 생성
    if not os.path.exists('logs'):
        os.makedirs('logs')
    # 로깅 설정 파일 로드 (프로젝트 루트 기준)
    logging.config.fileConfig('core/logging.conf', disable_existing_loggers=False)
else:
    # Vercel 환경에서는 기본 로깅 설정 (stdout) 사용
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(api_router, prefix="/api")

