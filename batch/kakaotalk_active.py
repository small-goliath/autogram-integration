import logging
import logging.config
from typing import List

logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# 카카오톡 채팅방 대화내용으로부터 일괄 댓글 및 좋아요
def main():
    logger.info("카카오톡 채팅방 대화내용으로부터 일괄 댓글 및 좋아요 배치를 시작합니다.")
    # 1. instagram_sessions 테이블에서 "doto.ri_" username의 
    # 2. "doto.ri_" 계정으로 로그인 시도

    try:
        insta = core.login_producer(username="doto.ri_")
        targets = kakaotalk_parsing.parsing()
    except Exception as e:
        log.error(f"품앗이를 할 수 없습니다.")
        discord.send_message(f"품앗이를 할 수 없습니다: [{e}]")

    for target in targets:
        try:
            count += 1
            if insta.username in str(target.username).split('@')[-1]:
                continue
            sleep_by_count(count=count, amount=5, sec=60)

            link = target.link
            media_id = insta.get_media_id(link)
            if insta.exists_comment(media_id=media_id, username=insta.username):
                continue
            media = insta.get_media(media_id)
            outsiders = get_outsiders()
            if media.user.username in outsiders:
                continue
            comment = gpt.generate_comment(media.caption_text)
            insta.comment(media_id, comment)
            insta.like(media_id)
        except CommentError as e:
            log.error(f"{insta.username} 계정으로 {link} 댓글달기 실패.")
            discord.send_message(f"{insta.username} 계정으로 {link} 댓글달기 실패 [{e}]")
        except LikeError as e:
            log.error(f"{insta.username} 계정으로 {link} 좋아요 실패.")
            discord.send_message(f"{insta.username} 계정으로 {link} 좋아요 실패 [{e}]")
        except Exception as e:
            log.error(f"{insta.username} 계정으로 {link} 품앗이 실패.")
            discord.send_message(f"{insta.username} 계정으로 {link} 품앗이 실패 [{e}]")

if __name__ == "__main__":
    main()
