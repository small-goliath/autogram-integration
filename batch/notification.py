import logging
import logging.config
import os
from discord_webhook.webhook import DiscordWebhook
from dotenv import load_dotenv
import tempfile

logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class Discord():
    MAX_MESSAGE_LENGTH = 1999

    def __init__(self):
        load_dotenv()
        self.uri = os.environ.get('WEBHOOK_URI')

    def send_message(self, message: str):
        logger.info(f"discord 알림 발송 중...")
        try:
            if len(message) > self.MAX_MESSAGE_LENGTH:
                with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as tmpfile:
                    tmpfile.write(message)
                    tmpfile_path = tmpfile.name

                webhook = DiscordWebhook(url=self.uri)
                with open(tmpfile_path, "rb") as f:
                    webhook.add_file(file=f.read(), filename="message.txt")
                webhook.execute()
                os.remove(tmpfile_path)
            else:
                discord = DiscordWebhook(url=self.uri, content=message)
                discord.execute()
        except Exception as e:
            logger.error("Failed discord notify!!!")
            logger.info(message)
            logger.error(str(e))

    def send_message_embeds(self, message: str, embeds: list):
        logger.info(f"discord 알림 발송 중...")
        discord = DiscordWebhook(url=self.uri, content=message, embeds=embeds)
        discord.execute()