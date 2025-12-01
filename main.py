from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os
import re
import yt_dlp

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "my_userbot")
VIDEO_CAPTION = os.getenv("VIDEO_CAPTION", "")

TIKTOK_REGEX = re.compile(r"(https?://)?(www\.)?(vm\.)?tiktok\.com", re.IGNORECASE)

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

def extract_tiktok_url(text: str) -> str:
    """Извлекает URL TikTok из текста"""
    # Ищем все возможные паттерны TikTok ссылок
    patterns = [
        r'https?://(?:www\.)?tiktok\.com/@[\w\.-]+/video/\d+',
        r'https?://(?:vm|vt)\.tiktok\.com/[\w\.-]+',
        r'https?://(?:www\.)?tiktok\.com/t/[\w\.-]+',
        r'https?://(?:www\.)?(?:vm\.)?tiktok\.com/[\w\.-]+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ""

async def download_tiktok_video(url: str) -> str:
    """Скачивает видео с TikTok и возвращает путь к файлу"""
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    # Создаем папку для загрузок
    os.makedirs('downloads', exist_ok=True)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@app.on_message(
    (filters.private) & (filters.text | filters.caption)
)
async def tiktok_handler(client: Client, message: Message):
    # игнорируем свои сообщения (userbot не трогает автора-аккаунта)
    if message.from_user and message.from_user.is_self:
        return

    text = message.text or message.caption or ""
    if not text:
        return

    if TIKTOK_REGEX.search(text):
        # Извлекаем URL TikTok
        tiktok_url = extract_tiktok_url(text)
        if not tiktok_url:
            return
        
        try:
            # Скачиваем видео
            video_path = await download_tiktok_video(tiktok_url)
            
            # Отправляем видео в ответ на исходное сообщение
            await client.send_video(
                chat_id=message.chat.id,
                video=video_path,
                caption=VIDEO_CAPTION if VIDEO_CAPTION else None,
                reply_to_message_id=message.id
            )
            
            # Удаляем файл после отправки
            try:
                os.remove(video_path)
            except Exception as e:
                print(f"Не удалось удалить файл {video_path}: {e}")
                
        except Exception as e:
            print(f"Ошибка при скачивании/отправке видео: {e}")

if __name__ == "__main__":
    app.run()
