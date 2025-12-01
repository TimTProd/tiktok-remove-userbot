from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os
import re

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "my_userbot")
REPLACE_TEXT = os.getenv(
    "REPLACE_TEXT",
    "Тут была ссылка на TikTok, но она была удалена."
)

TIKTOK_REGEX = re.compile(r"(https?://)?(www\.)?(vm\.)?tiktok\.com", re.IGNORECASE)

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(
    (filters.private) & (filters.text | filters.caption)
)
async def tiktok_blocker(client: Client, message: Message):
    # игнорируем свои сообщения (userbot не трогает автора-аккаунта)
    if message.from_user and message.from_user.is_self:
        return

    text = message.text or message.caption or ""
    if not text:
        return

    if TIKTOK_REGEX.search(text):
        # удаляем СООБЩЕНИЕ ОТ ДРУГОГО ПОЛЬЗОВАТЕЛЯ
        try:
            await message.delete()  # эквивалент delete_messages(chat_id, message.id)[web:29][web:30]
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")
            return

        # отправляем твой текст в чат
        try:
            await client.send_message(
                chat_id=message.chat.id,
                text=REPLACE_TEXT
            )
        except Exception as e:
            print(f"Не удалось отправить заменяющее сообщение: {e}")

if __name__ == "__main__":
    app.run()
