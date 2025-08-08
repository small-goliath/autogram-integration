import logging
import logging.config
import os
import re
import sys
from typing import List
import requests
from sqlalchemy.orm import Session
from instagrapi import Client
from batch.util import sleep_to_log
from core.db_transaction import read_only_transaction_scope, with_session
from core.service import (
    checkers_service,
    producers_service, 
    producer_instagram_service, 
    instagram_login_service
)
from batch import kakaotalk_parsing
from batch.notification import Discord
from dotenv import load_dotenv

from core.service.models import CheckerDetail, ProducerDetail

load_dotenv()
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
    discord = Discord()

    COMMENT_API_URL = os.getenv("COMMENT_API_URL")

    try:
        logged_in_producers: List[dict[str, Client | str]] = []
        logged_in_checkers: List[dict[str, Client | str]] = []
        with read_only_transaction_scope(db):
            # producer 계정 정보 조회
            producers: List[ProducerDetail] = producers_service.get_producers(db)
            if not producers:
                logger.error("producer 계정이 등록되어 있지 않습니다.")
                discord.send_message("producer 계정이 등록되어 있지 않습니다.")
                sys.exit(1)
            
            # producer 계정으로 로그인 시도
            for producer in producers:
                try:
                    producer_cl = producer_instagram_service.login_with_session_producer(producer.username, producer.session)
                    logged_in_producers.append({'client': producer_cl, 'username': producer.username})
                except Exception as e:
                    logger.error(f" producer 계정 '{producer.username}'으로 로그인 실패: {e}")
                    continue
            
            if not logged_in_producers:
                logger.error("모든 producer 계정으로 로그인에 실패했습니다.")
                discord.send_message("활동 검증 producer 계정 로그인 실패.")
                sys.exit(1)

            # checker 계정 정보 조회
            checkers: List[CheckerDetail] = checkers_service.get_checkers(db)
            if not checkers:
                logger.error("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
                discord.send_message("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
                sys.exit(1)

            # checker 계정으로 로그인 시도
            for checker in checkers:
                try:
                    cl = instagram_login_service.login_with_session(checker.username, checker.session)
                    logged_in_checkers.append({'client': cl, 'username': checker.username})
                except Exception as e:
                    logger.error(f" checker 계정 '{checker.username}'으로 로그인 실패: {e}")
                    continue
            
            if not logged_in_checkers:
                logger.error("모든 checker 계정으로 로그인에 실패했습니다.")
                discord.send_message("활동 검증 checker 계정 로그인 실패.")
                sys.exit(1)

        # 카카오톡 대화 내용으로부터 댓글 대상 조회
        logger.info("카카오톡 대화 내용 파싱을 시작합니다.")
        targets = kakaotalk_parsing.parsing()
        if not targets:
            logger.info("처리할 대상이 없습니다. 배치를 종료합니다.")
            return
        
        logger.info(f"총 {len(targets)}개의 대상을 처리합니다.")

        num_checkers = len(logged_in_checkers)
        for i, target in enumerate(targets):
            try:
                shortcode = get_shortcode_from_link(target.link)
                if not shortcode:
                    logger.warning(f"잘못된 URL입니다: {target.link}")
                    continue

                logger.info(f"게시물 처리 중: {target.link}")

                # Checker를 번갈아가며 media_info 조회
                media_info = None
                media_pk = None
                last_exception = None
                for j in range(num_checkers):
                    checker_index = (i + j) % num_checkers
                    checker_info = logged_in_checkers[checker_index]
                    cl = checker_info['client']
                    checker_username = checker_info['username']
                    try:
                        logger.info(f"'{checker_username}' 계정으로 media_info 조회 시도: {target.link}")
                        media_pk = cl.media_pk_from_code(shortcode)
                        media_info = cl.media_info(media_pk)
                        logger.info(f"'{checker_username}' 계정으로 media_info 조회 성공.")
                        break
                    except Exception as e:
                        last_exception = e
                        logger.warning(f"'{checker_username}' 계정으로 media_info 조회 실패: {e}. 다른 checker로 재시도합니다.")
                        sleep_to_log(10)
                        continue
                
                if not media_info:
                    error_message = f"'{target.link}' 링크 처리 중 모든 checker 계정으로 시도했으나 media_info 조회에 실패했습니다. 최종 오류: {last_exception}"
                    logger.error(error_message)
                    discord.send_message(error_message)
                    continue

                # 모든 producer가 좋아요 및 댓글 수행
                logger.info(f"게시물 {shortcode}에 모든 producer가 좋아요 및 댓글을 작성합니다.")
                comment_texts: List[str] = []
                for producer_info in logged_in_producers:
                    # 댓글 생성 API 호출
                    if media_info.caption_text:
                        logger.info("댓글 생성 API를 호출합니다.")
                        caption = str(media_info.caption_text).replace("\n", " ")
                        response = requests.post(COMMENT_API_URL, json={'text': caption, "pre_comments": comment_texts}, timeout=30)
                        response.raise_for_status()
                        comment_text = response.json().get("answer")
                    else:
                        comment_text = "멋져요! 😍"
                    
                    if not comment_text:
                        logger.error("댓글 생성에 실패했거나 유효하지 않은 응답입니다.")
                        continue

                    comment_texts.append(comment_text)
                    producer_cl = producer_info['client']

                    producer_username = producer_info['username']
                    if producer_username == target.username:
                        continue
                    
                    try:
                        logger.info(f"'{producer_username}' 계정으로 좋아요 및 댓글 작성 시도.")
                        producer_cl.media_like(media_pk)
                        sleep_to_log()
                        producer_cl.media_comment(media_pk, comment_text)
                        logger.info(f"'{producer_username}' 계정으로 좋아요 및 댓글 작성 완료.")
                        sleep_to_log()
                    except Exception as e:
                        logger.error(f"'{producer_username}' 계정으로 게시물 처리 중 오류 발생 ({target.link}): {e}", exc_info=True)
                        continue
            
            except Exception as e:
                logger.error(f"게시물 처리 중 오류 발생 ({target.link}): {e}", exc_info=True)
                continue

        logger.info("모든 작업 완료 후 producer 세션을 갱신합니다.")
        for producer_info in logged_in_producers:
            try:
                username = producer_info["username"]
                client: Client = producer_info["client"]
                session_string = client.dump_settings_to_string()
                producers_service.update_producer_session(db, username, session_string)
            except Exception as e:
                logger.error(f"'{username}' 계정의 세션 갱신 중 오류 발생: {e}", exc_info=True)
                continue

    except Exception as e:
        logger.critical(f"배치 실행 중 심각한 오류 발생: {e}", exc_info=True)
        discord.send_message(message=f"카카오톡 활성화 배치 실패: {e}")

    logger.info("카카오톡 채팅방 대화내용으로부터 일괄 댓글 및 좋아요 배치를 종료합니다.")

if __name__ == "__main__":
    main()
