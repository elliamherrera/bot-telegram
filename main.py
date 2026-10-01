import os
import asyncio
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ==========================================
# CONFIGURA AQUÍ TUS DATOS:
# ==========================================
TOKEN = "8727242775:AAG5OgBONPzVDekN7ycLZs1zuvDu8H4c2jI"        # Pega tu token entre las comillas
ADMIN_ID = 8962952054            # Cambia este número por tu ID (sin comillas)
# ==========================================

scheduler = AsyncIOScheduler()
estado_automatizacion = True

cronograma_dia = [
    {"hora": "10:00", "tipo": "🟢", "desc": "Temario Forex"},
    {"hora": "12:00", "tipo": "🔵", "desc": "Link Forex"},
    {"hora": "15:00", "tipo": "🟡", "desc": "Copy/Paste Binarias"},
    {"hora": "18:30", "tipo": "🔴", "desc": "LIVE en 30 min"},
    {"hora": "19:00", "tipo": "🔴", "desc": "Estamos en vivo"},
]

def construir_panel():
    estado = "▶️ Activa" if estado_automatizacion else "⏸️ Pausada"
    texto = f"🤖 **TELEGRAM AUTOMATION**\n**Estado:** {estado}\n\n📋 **Agenda de Hoy:**\n"
    for item in cronograma_dia:
        texto += f"• {item['tipo']} **{item['hora']}** — {item['desc']}\n"
    
    keyboard = [
        [InlineKeyboardButton("➕ Crear mensaje", callback_data="crear_msg"), InlineKeyboardButton("🔴 Programar LIVE", callback_data="prog_live")],
        [InlineKeyboardButton("🔗 Agregar link", callback_data="add_link"), InlineKeyboardButton("📅 Calendario", callback_data="ver_cal")],
        [InlineKeyboardButton("▶️ Activar" if not estado_automatizacion else "⏸️ Pausar", callback_data="toggle_estado")]
    ]
    return texto, InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    texto, markup = construir_panel()
    await update.message.reply_text(texto, reply_markup=markup, parse_mode="Markdown")

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global estado_automatizacion
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    
    if query.data == "toggle_estado":
        estado_automatizacion = not estado_automatizacion
        texto, markup = construir_panel()
        await query.edit_message_text(texto, reply_markup=markup, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botones))
    scheduler.start()
    app.run_polling()
