import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from groq import Groq

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация клиента Groq
# Ключ будет браться из переменных окружения GitHub Secrets
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Модель Groq (можно выбрать: llama3-8b-8192, llama3-70b-8192, mixtral-8x7b-32768)
MODEL_NAME = "llama3-8b-8192"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение при команде /start"""
    await update.message.reply_text(
        "👋 Привет! Я бот с искусственным интеллектом на базе Groq.\n"
        "Просто напиши мне любой вопрос, и я постараюсь ответить!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения и отправляет их в Groq"""
    user_text = update.message.text
    
    # Отправляем статус "печатает..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Запрос к Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Ты полезный и дружелюбный помощник. Отвечай на русском языке."
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=1024,
        )
        
        # Получаем ответ
        ai_response = chat_completion.choices[0].message.content
        
        # Отправляем ответ пользователю
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе к Groq: {e}")
        await update.message.reply_text(
            "😔 Произошла ошибка при обращении к нейросети. Попробуйте позже."
        )

def main():
    """Запуск бота"""
    # Получаем токен из переменных окружения
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("Не найден TELEGRAM_BOT_TOKEN!")
        return

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    logger.info("Бот запущен и слушает сообщения...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
