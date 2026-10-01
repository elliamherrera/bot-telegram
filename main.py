import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Configuración básica de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8962952054

# Identificador de tu canal o grupo principal para enviar recordatorios (ejemplo: "@tu_canal" o ID numérico)
CHANNEL_ID = os.getenv("CHANNEL_ID", "@tu_canal_oficial")

scheduler = AsyncIOScheduler()

# --- MENÚ INTERACTIVO ---
def main_keyboard(is_admin=False):
    keyboard = [
        [InlineKeyboardButton("📅 Horarios de Sesiones", callback_data="menu_horarios")],
        [InlineKeyboardButton("📈 Registro & Brokers", callback_data="menu_brokers")],
        [InlineKeyboardButton("📢 Canal Oficial", url="https://t.me/ElliamHerrera")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙️ Panel Admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(keyboard)

# --- TAREAS PROGRAMADAS (APScheduler) ---
async def recordatorio_sesion(context: ContextTypes.DEFAULT_TYPE):
    """Envia un mensaje automático al canal informando de una sesión en vivo."""
    mensaje = (
        "🚨 **¡ESTAMOS A PUNTO DE COMENZAR!** 🚨\n\n"
        "La sesión en vivo iniciará en 15 minutos.\n"
        "Prepara tu gráfica y conéctate a tiempo. 📈🔥"
    )
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=mensaje, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error al enviar recordatorio automático: {e}")

# --- HANDLERS DE COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = (user_id == ADMIN_ID)
    
    saludo = (
        "¡Bienvenido, Administrador! El bot está activo y listo."
        if is_admin else
        "¡Hola! Bienvenido al asistente oficial. Selecciona una opción del menú:"
    )
    
    await update.message.reply_text(
        saludo,
        reply_markup=main_keyboard(is_admin)
    )

async def enviar_comunicado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando exclusivo de admin para transmitir un mensaje al canal: /enviar Tu Mensaje Aquí"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ No tienes permisos para usar este comando.")
        return

    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("⚠️ Uso correcto: `/enviar Tu mensaje aquí`", parse_mode="Markdown")
        return

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=texto, parse_mode="Markdown")
        await update.message.reply_text("✅ Mensaje enviado exitosamente al canal.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar mensaje: {e}")

# --- HANDLER DE BOTONES (Callback) ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_horarios":
        texto = (
            "🕒 **Horarios de Sesiones en Vivo:**\n\n"
            "• **Lunes a Viernes (Mañana):** 9:00 AM AST\n"
            "• **Martes y Jueves (Noche):** 10:00 PM AST\n\n"
            "Mantén activadas las notificaciones del canal."
        )
        await query.message.edit_text(texto, parse_mode="Markdown", reply_markup=main_keyboard(query.from_user.id == ADMIN_ID))

    elif query.data == "menu_brokers":
        texto = (
            "📊 **Plataformas Recomendadas & Registros:**\n\n"
            "Accede a los enlaces oficiales de registro y herramientas de trading."
        )
        await query.message.edit_text(texto, parse_mode="Markdown", reply_markup=main_keyboard(query.from_user.id == ADMIN_ID))

    elif query.data == "menu_admin":
        texto = (
            "🛠 **Panel de Control:**\n\n"
            "Usa el comando `/enviar <mensaje>` para publicar directamente en el canal."
        )
        await query.message.edit_text(texto, parse_mode="Markdown", reply_markup=main_keyboard(True))

# --- POST INIT (Configuración de Scheduler) ---
async def post_init(application):
    # Programar recordatorio recurrente (Ejemplo: Lunes a Viernes a las 08:45 AM)
    scheduler.add_job(
        recordatorio_sesion,
        trigger='cron',
        day_of_week='mon-fri',
        hour=8,
        minute=45,
        args=[application]
    )
    scheduler.start()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enviar", enviar_comunicado))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
