import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import ollama
import nest_asyncio
from dotenv import load_dotenv
import os

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv('TOKEN')

context_memory = {}

async def start(update: Update, context) -> None:
    await update.message.reply_text('Привет! Я чат-бот на базе Llama. Чем могу помочь?')

async def handle_message(update: Update, context):
    user_id = update.effective_user.id

    if user_id not in context_memory:
        context_memory[user_id] = []

    # Добавляем сообщение пользователя в историю
    context_memory[user_id].append({
        'role': 'user',
        'content': update.message.text
    })

    # Храним только последние 8 сообщений
    context_memory[user_id] = context_memory[user_id][-8:]

    # Отправляем в ollama
    response = ollama.chat(
        model='gemma3:1b',
        messages=context_memory[user_id]
    )

    reply = response['message']['content']

    # Добавляем ответ бота в историю
    context_memory[user_id].append({
        'role': 'assistant',
        'content': reply
    })

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен...")
app.run_polling()