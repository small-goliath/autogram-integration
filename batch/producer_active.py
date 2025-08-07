import logging
import logging.config
import os
import random
import re
import sys
import time
from typing import List

import requests
from dotenv import load_dotenv
from instagrapi import Client
from sqlalchemy.orm import Session

from batch.notification import Discord
from batch.util import sleep_to_log
from core.db_transaction import read_only_transaction_scope, with_session
from core.service import (
    checkers_service,
    consumer_service,
    instagram_login_service,
    producer_instagram_service,
    producers_service,
)
from core.service.models import CheckerDetail, ConsumerDetail, ProducerDetail

load_dotenv()
logging.config.fileConfig("batch/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


@with_session
def main(db: Session):
    """
    producer가 consumer들의 최신 게시물에 대해 일괄 댓글 및 좋아요를 수행합니다.
    """
    logger.info("producer로부터 일괄 댓글 및 좋아요 배치를 시작합니다.")
    discord = Discord()
    COMMENT_API_URL = os.getenv("COMMENT_API_URL")

    try:
        with read_only_transaction_scope(db):
            # producer 계정 정보 조회
            producers: List[ProducerDetail] = producers_service.get_producers(db)
            if not producers:
                logger.error("producer 계정이 등록되어 있지 않습니다.")
                discord.send_message("producer 계정이 등록되어 있지 않습니다.")
                sys.exit(1)

            # producer 계정으로 로그인 시도
            logged_in_producers: List[dict[str, Client | str]] = []
            for producer in producers:
                try:
                    producer_cl = (
                        producer_instagram_service.login_with_session_producer(
                            producer.username, producer.session
                        )
                    )
                    logged_in_producers.append(
                        {"client": producer_cl, "username": producer.username}
                    )
                except Exception as e:
                    logger.error(f" producer 계정 '{producer.username}'으로 로그인 실패: {e}")
                    continue

            if not logged_in_producers:
                logger.error("모든 producer 계정으로 로그인에 실패했습니다.")
                discord.send_message("활동 producer 계정 로그인 실패.")
                sys.exit(1)

            # checker 계정 정보 조회
            checkers: List[CheckerDetail] = checkers_service.get_checkers(db)
            if not checkers:
                logger.error("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
                discord.send_message("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
                sys.exit(1)

            # checker 계정으로 로그인 시도
            logged_in_checkers: List[dict[str, Client | str]] = []
            for checker in checkers:
                try:
                    cl = instagram_login_service.login_with_session(
                        checker.username, checker.session
                    )
                    logged_in_checkers.append(
                        {"client": cl, "username": checker.username}
                    )
                except Exception as e:
                    logger.error(f" checker 계정 '{checker.username}'으로 로그인 실패: {e}")
                    continue

            if not logged_in_checkers:
                logger.error("모든 checker 계정으로 로그인에 실패했습니다.")
                discord.send_message("활동 검증 checker 계정 로그인 실패.")
                sys.exit(1)

            consumers: List[ConsumerDetail] = consumer_service.get_consumers(db)
            if not consumers:
                logger.info("처리할 consumer가 없습니다. 배치를 종료합니다.")
                return

        logger.info(f"총 {len(consumers)}명의 consumer를 처리합니다.")
        num_checkers = len(logged_in_checkers)

        for i, consumer in enumerate(consumers):
            # Checker를 번갈아가며 consumer의 최근 게시물 4개 가져오기
            medias = []
            last_exception = None
            for j in range(num_checkers):
                checker_index = (i + j) % num_checkers
                checker_info = logged_in_checkers[checker_index]
                cl = checker_info["client"]
                checker_username = checker_info["username"]
                try:
                    logger.info(f"'{checker_username}' 계정으로 '{consumer.username}'의 최근 게시물 조회 시도.")
                    user_id = cl.user_id_from_username(username=consumer.username)
                    medias = cl.user_medias(user_id=user_id, amount=4, sleep=3)
                    logger.info(f"'{checker_username}' 계정으로 '{consumer.username}'의 게시물 {len(medias)}개 조회 성공.")
                    break
                except Exception as e:
                    last_exception = e
                    logger.warning(f"'{checker_username}' 계정으로 '{consumer.username}'의 게시물 조회 실패: {e}. 다른 checker로 재시도합니다.")
                    sleep_to_log(10)
                    continue
            
            if not medias:
                error_message = f"'{consumer.username}'의 게시물 조회에 모든 checker가 실패했습니다. 최종 오류: {last_exception}"
                logger.error(error_message)
                discord.send_message(error_message)
                continue

            for media in medias:
                try:
                    logger.info(f"게시물 처리 중: https://www.instagram.com/p/{media.code}")

                    # Checker를 번갈아가며 댓글 중복 확인
                    commenting_usernames = set()
                    if logged_in_checkers:
                        comments_fetched = False
                        last_comment_exception = None
                        for j in range(num_checkers):
                            checker_index = (i + j) % num_checkers
                            checker_info = logged_in_checkers[checker_index]
                            checker_cl = checker_info["client"]
                            checker_username = checker_info["username"]
                            try:
                                logger.info(f"'{checker_username}' 계정으로 게시물 {media.code}의 댓글 목록 조회 시도.")
                                comments = checker_cl.media_comments(media.pk)
                                commenting_usernames = {c.user.username for c in comments}
                                logger.info(f"'{checker_username}' 계정으로 게시물 {media.code}의 기존 댓글 {len(commenting_usernames)}개 확인.")
                                comments_fetched = True
                                break
                            except Exception as e:
                                last_comment_exception = e
                                logger.warning(f"'{checker_username}' 계정으로 게시물 {media.code}의 댓글을 가져오는 데 실패했습니다: {e}. 다른 checker로 재시도합니다.")
                                continue
                            finally:
                                sleep_to_log()
                        
                        if not comments_fetched:
                            logger.warning(f"게시물 {media.code}의 댓글을 가져오는 데 모든 checker가 실패했습니다. 최종 오류: {last_comment_exception}. 댓글 중복 확인을 건너뜁니다.")

                    # 모든 producer가 좋아요 및 댓글 수행
                    logger.info(f"게시물 {media.code}에 모든 producer가 좋아요 및 댓글을 작성합니다.")
                    for producer_info in logged_in_producers:
                        producer_username = producer_info["username"]
                        if producer_username == media.user.username or producer_username in commenting_usernames:
                            continue
                        
                        # 댓글 생성 API 호출
                        if media.caption_text:
                            logger.info("댓글 생성 API를 호출합니다.")
                            caption = str(media.caption_text).replace("\n", " ")
                            response = requests.post(
                                COMMENT_API_URL, json={"text": caption}, timeout=30
                            )
                            response.raise_for_status()
                            comment_text = response.json().get("answer")
                        else:
                            comment_text = "멋져요! 😍"

                        if not comment_text:
                            logger.error("댓글 생성에 실패했거나 유효하지 않은 응답입니다.")
                            continue

                        producer_cl = producer_info["client"]
                        try:
                            logger.info(f"'{producer_username}' 계정으로 좋아요 및 댓글 작성 시도.")
                            producer_cl.media_like(media.pk)
                            sleep_to_log(30)
                            producer_cl.media_comment(media.pk, comment_text)
                            logger.info(f"'{producer_username}' 계정으로 좋아요 및 댓글 작성 완료.")
                            sleep_to_log(60)
                        except Exception as e:
                            logger.error(f"'{producer_username}' 계정으로 게시물 처리 중 오류 발생 (https://www.instagram.com/p/{media.code}): {e}", exc_info=True)
                            continue
                
                except Exception as e:
                    logger.error(f"게시물 처리 중 오류 발생 (https://www.instagram.com/p/{media.code}): {e}", exc_info=True)
                    continue

    except Exception as e:
        logger.critical(f"producer 배치 실행 중 심각한 오류 발생: {e}", exc_info=True)
        discord.send_message(message=f"producer 배치 실패: {e}")

    logger.info("producer로부터 일괄 댓글 및 좋아요 배치를 종료합니다.")


if __name__ == "__main__":
    main()
