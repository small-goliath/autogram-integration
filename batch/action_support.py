
import logging
from typing import List, Set

from instagrapi import Client
from instagrapi.types import Comment, Media
from sqlalchemy.orm import Session

from batch.util import sleep_to_log
from core.service import checkers_service, producers_service


logger = logging.getLogger(__name__)

class Action:
    def __init__(self, cl: Client):
        self.cl = cl
    
    def media_pk(self, shortcode: str) -> str:
        logger.info(f"{shortcode}의 미디어 식별자를 가져옵니다.")
        return self.cl.media_pk_from_code(shortcode)
    
    def get_commenters(self, media_pk: str, max_amount: int = 100) -> Set[Comment]:
        logger.info(f"{media_pk}의 댓글을 {max_amount}씩 모두 가져옵니다.")
        comments: List[Comment] = []
        min_id = None
        while True:
            comments_chunk, next_min_id = self.cl.media_comments_chunk(
                media_pk, max_amount=max_amount, min_id=min_id
            )
            comments.extend(comments_chunk)
            if not next_min_id:
                break
            min_id = next_min_id
            sleep_to_log(1)
        return {comment.user.username for comment in comments}
    
    def checker_update_session(self, db: Session):
        logger.info(f"{self.cl.username}의 세션을 갱신합니다.")
        try:
            checkers_service.update_session(db, self.cl.username, self.cl.get_settings())
        except Exception as e:
            logger.error(f"'{self.cl.username}' 계정의 세션 갱신 중 오류 발생: {e}")
            raise

    def producer_update_session(self, db: Session):
        logger.info(f"{self.cl.username}의 세션을 갱신합니다.")
        try:
            producers_service.update_session(db, self.cl.username, self.cl.get_settings())
        except Exception as e:
            logger.error(f"'{self.cl.username}' 계정의 세션 갱신 중 오류 발생: {e}")
            raise

    def media_info(self, media_pk: str) -> Media:
        logger.info(f"{media_pk}의 정보를 가져옵니다.")
        return self.cl.media_info(media_pk)
    
    def media_like(self, media_pk: str):
        logger.info(f"{self.cl.username} 계정으로 {media_pk}를 좋아요 중...")
        self.cl.media_like(media_pk)

    def media_comment(self, media_pk: str, comment: str):
        logger.info(f"{self.cl.username} 계정으로 {media_pk}에 댓글 작성 중...")
        self.cl.media_comment(media_pk, comment)

    def user_id_from_username(self, username: str):
        logger.info(f"{username}의 유저 식별자를 가져옵니다.")
        return self.cl.user_id_from_username(username=username)
    
    def user_medias(self, user_id: str, amount: int = 4, sleep: int = 3) -> List[Media]:
        logger.info(f"{user_id}의 최근 {amount}개의 피드를 가져옵니다.")
        return self.cl.user_medias(user_id=user_id, amount=amount, sleep=sleep)