import logging
import logging.config
import random
import re
import time
import requests
from instaloader import Post
from sqlalchemy.orm import Session
from core.db_transaction import read_only_transaction_scope, with_session
from core.service import (
    producers_service, 
    producer_instagram_service, 
    instagramloader_session_service,
    instagramloader_login_service
)
from batch import kakaotalk_parsing
from batch.notification import Discord

logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def get_shortcode_from_link(link: str) -> str | None:
    """Instagram 링크에서 shortcode를 추출합니다."""
    match = re.search(r"/(p|reel)/([^/]+)", link)
    return match.group(2) if match else None

@with_session
def main(db: Session):
    """
    카카오톡 채팅방 대화내용으로부터 일괄 댓글 및 좋아요를 수행합니다.
    """
    logger.info("카카오톡 채팅방 대화내용으로부터 일괄 댓글 및 좋아요 배치를 시작합니다.")
    
    PRODUCER_USERNAME = "doto.ri_"
    CHECKER_USERNAME = "muscle.er"
    COMMENT_API_URL = "http://124.58.209.123:18002/api/comments/query"

    try:
        # 1. producer, checker 로그인
        with read_only_transaction_scope(db):
            logger.info(f"'{PRODUCER_USERNAME}' 계정으로 로그인을 시도합니다.")
            producer = producers_service.get_producer(db, PRODUCER_USERNAME)
            if not producer or not producer.session:
                raise Exception(f"'{PRODUCER_USERNAME}'의 세션 정보를 찾을 수 없습니다.")
            cl = producer_instagram_service.login_with_session_producer(producer.username, producer.session)
            logger.info(f"'{PRODUCER_USERNAME}' 계정으로 로그인 성공.")

            logger.info(f"'{CHECKER_USERNAME}' 계정으로 로그인을 시도합니다.")
            session_string = instagramloader_session_service.get_session_string(db, CHECKER_USERNAME)
            if not session_string:
                raise Exception(f"'{CHECKER_USERNAME}'의 세션 정보를 찾을 수 없습니다.")
            L = instagramloader_login_service.login_with_session(CHECKER_USERNAME, session_string)
            logger.info(f"'{CHECKER_USERNAME}' 계정으로 로그인 성공.")

        # 2. batch.kakaotalk_parsing의 parsing() 함수로부터 좋아요 및 댓글 대상 조회
        logger.info("카카오톡 대화 내용 파싱을 시작합니다.")
        targets = kakaotalk_parsing.parsing()
        if not targets:
            logger.info("처리할 대상이 없습니다. 배치를 종료합니다.")
            return
        
        logger.info(f"총 {len(targets)}개의 대상을 처리합니다.")

        for target in targets:
            try:
                shortcode = get_shortcode_from_link(target.link)
                if not shortcode:
                    logger.warning(f"잘못된 URL입니다: {target.link}")
                    continue

                logger.info(f"게시물 처리 중: {target.link}")
                
                # 3. media_id 조회
                media_id = producer_instagram_service.media_id(cl, shortcode)

                # 4. 댓글 생성 API 호출
                post = Post.from_shortcode(L.context, shortcode)
                if post.caption:
                    logger.info("댓글 생성 API를 호출합니다.")
                    caption = str(post.caption).replace("\n", " ")
                    response = requests.post(COMMENT_API_URL, json={'text': caption}, timeout=30)
                    response.raise_for_status()
                    comment_text = response.json().get("answer")
                else:
                    comment_text = "멋져요! 😍"
                
                if not comment_text:
                    logger.error("댓글 생성에 실패했거나 유효하지 않은 응답입니다.")
                    continue

                # 5. 좋아요 및 댓글 수행
                logger.info(f"게시물 {shortcode}에 좋아요 및 댓글을 작성합니다.")
                producer_instagram_service.like(cl, media_id)
                time.sleep(random.uniform(3, 7)) # 좋아요와 댓글 사이의 간격
                producer_instagram_service.comment(cl, media_id, comment_text)

                # 인스타그램의 제한을 피하기 위해 랜덤 딜레이 추가
                sleep_time = random.uniform(10, 20)
                logger.info(f"{sleep_time:.2f}초 대기합니다.")
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"게시물 처리 중 오류 발생 ({target.link}): {e}", exc_info=True)
                continue # 다음 대상으로 넘어감

    except Exception as e:
        logger.critical(f"배치 실행 중 심각한 오류 발생: {e}", exc_info=True)
        Discord().send_message(message=f"카카오톡 활성화 배치 실패: {e}")

    logger.info("카카오톡 채팅방 대화내용으로부터 일괄 댓글 및 좋아요 배치를 종료합니다.")

if __name__ == "__main__":
    main()