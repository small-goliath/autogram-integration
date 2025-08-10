import locale
from datetime import datetime, timedelta, timezone
import logging
import os
from time import sleep
from typing import List
from dotenv import load_dotenv
import random


logger = logging.getLogger(__name__)

def get_today() -> datetime:
    locale.setlocale(locale.LC_TIME, 'ko_KR.UTF-8')
    KST = timezone(timedelta(hours=9))
    return datetime.now(KST)

def get_formatted_today(format: str) -> datetime:
    return get_today().strftime(format)
    
def get_outsiders() -> List[str]:
    load_dotenv()
    return [item.strip() for item in os.getenv('OUTSIDERS', '').split(',') if item.strip()]
    
def sleep_by_count(count: int, amount: int, sec: int):
    if count % amount == 0:
        sleep_to_log(sec)

def sleep_to_log(sec: int = 0):
    if sec == 0:
        sec = random.randint(150, 120)
    logger.info(f"{sec}초 중단.")
    sleep(sec)