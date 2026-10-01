import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8962952054

scheduler = AsyncIOScheduler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        await update.message.reply_text("¡Bienvenido, Administrador! El bot está activo y listo para gestionar el canal.")
    else:
        await update.message.reply_text("¡Hola! Soy el asistente oficial del canal. Mantente atento a los recordatorios y sesiones.")

async def post_init(application):
    scheduler.start()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
