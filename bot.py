from dotenv import load_dotenv
import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from openai import AsyncOpenAI # Нужен openai-совместимый api

load_dotenv()

# Продцепляем переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Токен бота (из .env)

# Ваши данные polza.ai (из .env)
POLZA_API_KEY = os.getenv("POLZA_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")
POLZA_BASE_URL = os.getenv("POLZA_BASE_URL")

# Логи бота (можно закомментить, если они не нужны)
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    filemode="a",
    filename="bot.log"
)

bot = Bot(token=TELEGRAM_BOT_TOKEN)

dp = Dispatcher()

router = Router()

client = AsyncOpenAI(
  base_url=POLZA_BASE_URL,
  api_key=POLZA_API_KEY,
)

# Важно: порядок регистрации = порядок проверки.
# CommandStart должен идти раньше общего хендлера, иначе /start уйдёт в модель.
@router.message(CommandStart())
async def start(message: Message):
    try:
        logging.info(
            f"/start от user_id={message.from_user.id} "
            f"username={message.from_user.username} "
        )
        await message.answer("Ку-ку. Я создан для того, чтобы тратить деньги с баланса моего создателя за каждый запрос/ответ)")
        logging.info("Ответ на /start был отправлен") # Логи
    except Exception as e:
        logging.error(f"Ошибка в /start: {e}") # Логи


@router.message()
async def chat(message: Message):
    if not message.text:
        await message.answer("Извини, но пока что я могу отвечать только на текстовые сообщения. Деньги со счёта разработчика не списались(((")
        return
    try:
        response = await client.responses.create(
            model=AI_MODEL,
            input=message.text
        )
        await message.answer(response.output_text)
    except Exception as e:
        print("Ошибка: ", e) # Логи


async def main():
    try:
        logging.info("Запуск бота...") # Логи
        me = await bot.get_me()
        logging.info(f"Подключено как @{me.username}") # Логи
        dp.include_router(router)
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"Ошибка при старте: {e}") # Логи

if __name__ == "__main__":
    asyncio.run(main())
