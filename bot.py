import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ключ Hugging Face из переменных окружения
HF_TOKEN = os.environ.get("HF_TOKEN")

# Модель на Hugging Face (можно менять)
MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот с ИИ на базе Hugging Face.\n"
        "Напиши мне любой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": user_text,
        "parameters": {"max_new_tokens": 512, "temperature": 0.7}
    }

    try:
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=30)
        result = response.json()

        # Парсим ответ от Hugging Face
        if isinstance(result, list) and len(result) > 0:
            ai_response = result[0].get("generated_text", "Не удалось получить ответ.")
        elif isinstance(result, dict) and "error" in result:
            ai_response = f"Ошибка: {result['error']}"
        else:
            ai_response = "Не удалось получить ответ от модели."

        await update.message.reply_text(ai_response)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("😔 Ошибка при обращении к ИИ. Попробуйте позже.")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Не найден TELEGRAM_BOT_TOKEN!")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
