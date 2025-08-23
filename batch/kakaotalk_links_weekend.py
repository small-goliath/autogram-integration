import logging
import logging.config
import sys


from batch.kakaotalk_parsing import parsing
from batch.notification import Discord
from core.db_transaction import transactional
from core.service import request_by_week_service

logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def run_batch():
    """
    카카오톡 대화 내용을 파싱하여 주간 요청 테이블을 업데이트하는 배치 작업을 실행합니다.
    """
    logger.info("주간 카카오톡 링크 집계 배치를 시작합니다.")
    discord = Discord()
    
    try:
        with transactional() as db:
            # 1. 카카오톡 대화 내용 파싱
            parsed_links = parsing()
            if not parsed_links:
                logger.info("파싱된 링크가 없어 배치를 종료합니다.")
                return

            logger.info(f"총 {len(parsed_links)}개의 링크를 파싱했습니다.")

            # 2. 서비스 레이어를 통해 데이터베이스 업데이트
            request_by_week_service.update_request_by_week(db, parsed_links)

        summary = f"주간 카카오톡 링크 집계 배치 완료: 총 {len(parsed_links)}개의 링크 처리"
        logger.info(summary)
        discord.send_message(summary)

    except Exception as e:
        error_message = f"배치 실행 중 오류 발생: {e}"
        logger.error(error_message)
        discord.send_message(error_message)
        sys.exit(1)

if __name__ == "__main__":
    run_batch()
