from collections import defaultdict
import logging
import logging.config
import os
import re
import sys
import locale
from datetime import timedelta

from batch.models import KakaoTalk
from batch.notification import Discord
from batch.util import get_today

# 카카오톡 대화내용 파싱
logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')

def get_target_week_dates():
    today = get_today()
    last_monday = today - timedelta(days=today.weekday() + 7)
    this_monday = today - timedelta(days=today.weekday())
    return last_monday, this_monday

def format_date(date):
    return date.strftime("%Y년 %-m월 %-d일 %A")

def parsing() -> list[KakaoTalk]:
    kakaotalk_file = "batch/kakaotalk/KakaoTalk_latest.txt"
    logger.info(f"Processing file: {kakaotalk_file}")
    if not os.path.exists(kakaotalk_file):
        logger.info("최신 카카오톡 대화방 내용이 없습니다.")
        return
    
    start_date, end_date = get_target_week_dates()
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    logger.info(f"타겟은 {formatted_start} 부터 {formatted_end} 전날까지 입니다.")

    is_last_week = False

    try:
        # 대화방 내용 중 지난주 내용만 체크
        chat = ""
        with open(kakaotalk_file, 'r', encoding='utf-8') as f:
            for line in f:
                # chat += line
                if is_last_week:
                    chat += line
                if line.strip() == formatted_start:
                    is_last_week = True
                elif line.strip() == formatted_end:
                    break

        # 품앗이 대상 피드/릴스 캐치
        message_pattern = re.compile(
            r"""^
            (20\d{2}\.\s*\d{1,2}\.\s*\d{1,2})         # 날짜
            (?:.*?)                                     # 0개 이상의 문자
            ,\s                                       # 콤마와 공백
            (.*?)                                     # 닉네임
            \s*:\s                                    # 공백과 콜론
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # 날짜가 아닌 0개 이상의 문자열
            (https://www\.instagram\.com/[^\s\n]+)    # 인스타그램 링크
            \n+                                       # 1개 이상의 줄바꿈
            (?:(?!20\d{2}\.\s*\d{1,2}\.\s*\d{1,2}).)*?  # 날짜가 아닌 0개 이상의 문자열
            /(?P<digit>\d+)
            """,
            re.MULTILINE | re.VERBOSE
        )

        # 인스타그램 링크 맵핑
        kakaotalk_parsed = []
        messages = message_pattern.findall(chat)
        for match in messages:
            kakaotalk_parsed.append(KakaoTalk(
                username=match[1],
                link=str(match[2]).strip()
            ))

        return kakaotalk_parsed

    except Exception as e:
        logger.error(f"Batch failure: {e}")
        Discord().send_message(message=f"Batch failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Parsing KakaoTalk chat history...")
    result = parsing()
    username_links = defaultdict(list)

    for t in result:
        username_links[t.username].append(t.link)

    for username, links in username_links.items():
        logger.info(f"{username}: {len(links)}개")
        for link in links:
            logger.info(link)
