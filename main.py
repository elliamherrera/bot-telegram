import os
import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

# Configuración de Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8962952054
CHANNEL_ID = os.getenv("CHANNEL_ID", "@ElliamHerrera")

# Zona Horaria de República Dominicana
TIMEZONE = pytz.timezone("America/Santo_Domingo")

scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# ==============================================================================
# 1. PLANTILLAS Y CONFIGURACIÓN DE SESIONES EN VIVO
# ==============================================================================

LIVE_TEMPLATES_PRE = {
    "FOREX": (
        "☀️ Buenas tardes familia\n\n"
        "Nos vemos en 30 minutos 🏌🏻🏌🏻\n\n"
        "Forex (CFD)\n\n"
        "🇩🇴🇻🇪 10:00 AM\n"
        "🇦🇷🇺🇾🇨🇱 11:00 AM\n"
        "🇵🇪 9:00 AM\n"
        "🇬🇹🇲🇽 8:00 AM\n\n"
        "Link: {link}"
    ),
    "BINARIAS": (
        "🌙 Buenas noches familia\n\n"
        "Nos vemos en 30 minutos 🏌🏻🏌🏻\n\n"
        "Opciones Binarias\n\n"
        "🇩🇴🇻🇪 {hora_do}\n"
        "🇦🇷🇺🇾🇨🇱 {hora_ar}\n"
        "🇵🇪 {hora_pe}\n"
        "🇬🇹🇲🇽 {hora_gt}\n\n"
        "Link: {link}"
    ),
    "EDUCATIVA": (
        "🏌🏻🏌🏻 Buenas tardes familia\n\n"
        "Nos vemos en 30 minutos 👀\n\n"
        "Sesión Educativa\n\n"
        "🇩🇴🇻🇪 3:00 PM\n"
        "🇦🇷🇺🇾🇨🇱 4:00 PM\n"
        "🇵🇪 2:00 PM\n"
        "🇬🇹🇲🇽 1:00 PM\n\n"
        "Link: {link}"
    ),
    "CRIPTO": (
        "🏌🏻🏌🏻 Buenas tardes familia\n\n"
        "Nos vemos en 30 minutos 👀\n\n"
        "Cripto Binarias\n\n"
        "🇩🇴🇻🇪 3:00 PM\n"
        "🇦🇷🇺🇾🇨🇱 4:00 PM\n"
        "🇵🇪 2:00 PM\n"
        "🇬🇹🇲🇽 1:00 PM\n\n"
        "Link: {link}"
    )
}

LIVE_TEMPLATES_NOW = {
    "FOREX": (
        "🏌🏻🏌🏻 YA ESTAMOS EN VIVO 🔴\n\n"
        "Forex (CFD)\n\n"
        "Entra aquí 👇\n"
        "{link}"
    ),
    "BINARIAS": (
        "🌙🏌🏻🏌🏻 YA ESTAMOS EN VIVO 🔴\n\n"
        "Opciones Binarias\n\n"
        "Entra aquí 👇\n"
        "{link}"
    ),
    "EDUCATIVA": (
        "🏌🏻🏌🏻 YA ESTAMOS EN VIVO 🔴\n\n"
        "Sesión Educativa\n\n"
        "Entra aquí 👇\n"
        "{link}"
    ),
    "CRIPTO": (
        "🏌🏻🏌🏻 YA ESTAMOS EN VIVO 🔴\n\n"
        "Cripto Binarias\n\n"
        "Entra aquí 👇\n"
        "{link}"
    )
}

# SESIONES EN VIVO DESACTIVADAS TEMPORALMENTE ("active": False)
LIVE_SCHEDULE = [
    {
        "active": False,
        "days": "mon-thu",
        "hour": 10,
        "minute": 0,
        "type": "FOREX",
        "link": "https://minedacademy.com/academy/Trading_Pro/Forex/Canal/79/220/Elliam_Herrera"
    },
    {
        "active": False,
        "days": "sun",
        "hour": 20,
        "minute": 0,
        "type": "BINARIAS",
        "horas": ("8:00 PM", "9:00 PM", "7:00 PM", "6:00 PM"),
        "link": "https://minedacademy.com/academy/Trading_Pro/Binarias/Canal/78/219/Elliam_Herrera"
    },
    {
        "active": False,
        "days": "mon,tue",
        "hour": 21,
        "minute": 0,
        "type": "BINARIAS",
        "horas": ("9:00 PM", "10:00 PM", "8:00 PM", "7:00 PM"),
        "link": "https://minedacademy.com/academy/Trading_Pro/Binarias/Canal/78/219/Elliam_Herrera"
    },
    {
        "active": False,
        "days": "wed",
        "hour": 20,
        "minute": 0,
        "type": "BINARIAS",
        "horas": ("8:00 PM", "9:00 PM", "7:00 PM", "6:00 PM"),
        "link": "https://minedacademy.com/academy/Trading_Pro/Binarias/Canal/78/219/Elliam_Herrera"
    },
    {
        "active": False,
        "days": "fri,sun",
        "hour": 15,
        "minute": 0,
        "type": "EDUCATIVA",
        "link": "https://minedacademy.com/academy/Trading_Pro/Forex/Canal/79/220/Elliam_Herrera"
    },
    {
        "active": False,
        "days": "sat",
        "hour": 15,
        "minute": 0,
        "type": "CRIPTO",
        "link": "https://minedacademy.com/academy/Trading_Pro/Binarias/Canal/78/219/Elliam_Herrera"
    }
]

# ==============================================================================
# 2. CONFIGURACIÓN CENTRALIZADA DE PUBLICACIONES PROMOCIONALES AUTOMÁTICAS (ACTIVAS)
# ==============================================================================
PROMO_CONFIG = {
    "PROMO_BINARIAS": {
        "active": True,
        "days": "mon,wed,fri,sun",
        "hour": 17,
        "minute": 0,
        "day_of_month": None,
        "text": (
            "🏌🏻🏌🏻 ¿Todavía no tienes un broker para operar opciones binarias?\n\n"
            "Aquí tienes una opción con pagos de hasta 85%, además de depósito y retiro mediante USDT.\n\n"
            "Broker de Binarias\n"
            "👉 https://app.worldbinary.pro/auth/signup?ibCode=ELIAM"
        )
    },
    "PROMO_FOREX": {
        "active": True,
        "days": "tue,thu,sat",
        "hour": 17,
        "minute": 0,
        "day_of_month": None,
        "text": (
            "🏌🏻🏌🏻 Si todavía no tienes tu cuenta de trading para hacer CFD, aquí tienes diferentes opciones:\n\n"
            "Broker de Forex / Capital propio\n"
            "👉 https://portal.impulseworld.pro/register?ibid=57806\n\n"
            "Cuentas de Fondeo\n"
            "👉 https://app-trader.impulseworld.pro/r/register?sponsorCode=Elliam"
        )
    },
    "MONEY_NIGHT_PRE": {
        "active": False,
        "days": "thu",
        "hour": 22,
        "minute": 30,
        "day_of_month": None,
        "text": (
            "🌙🏌🏻🏌🏻 Buenas noches familia\n\n"
            "Nos vemos en 30 minutos 👀\n\n"
            "Money Night\n"
            "Todos los educadores juntos trabajando en todos los mercados.\n\n"
            "Link:\n"
            "https://minedacademy.com/academy/Trading_Pro/Money%20Night/Canal/95/259/Money_Night"
        )
    },
    "MONEY_NIGHT_NOW": {
        "active": False,
        "days": "thu",
        "hour": 23,
        "minute": 0,
        "day_of_month": None,
        "text": (
            "🌙🏌🏻🏌🏻 YA ESTAMOS EN VIVO 🔴\n\n"
            "Money Night\n"
            "Todos los educadores juntos trabajando en todos los mercados.\n\n"
            "Entra aquí 👇\n"
            "https://minedacademy.com/academy/Trading_Pro/Money%20Night/Canal/95/259/Money_Night"
        )
    },
    "RUTA_INICIO": {
        "active": True,
        "days": None,
        "hour": 10,
        "minute": 30,
        "day_of_month": "2,17",
        "text": (
            "🚀 Si ya acabas de firmar clientes con TradingPro, aquí te dejo la Ruta de Inicio Oficial para que tu comunidad arranque sin perder tiempo.\n\n"
            "🔗 https://rutadeinicio.lovable.app\n\n"
            "En esta ruta tu equipo encontrará:\n"
            "✅ Inducción completa de cómo navegar TradingPro por dentro\n"
            "✅ Cómo utilizar los escáneres e indicadores\n"
            "✅ Cómo copiar y pegar en Forex\n"
            "✅ Cómo copiar y pegar en Opciones Binarias\n"
            "✅ Horarios oficiales de las sesiones\n"
            "✅ Testimonios e imágenes con resultados reales de otros clientes\n\n"
            "📌 Solo tienes que enviar este link a cada nuevo y ya tendrán una guía clara para empezar desde el día 1.\n"
            "Guárdalo en destacado y úsalo con todos tus nuevos. 🚀🔥"
        )
    },
    "PROMO_TEMARIO": {
        "active": True,
        "days": "sat,sun",
        "hour": 10,
        "minute": 30,
        "day_of_month": None,
        "text": (
            "🚨 Familia, quiero que me ayuden a mover esto con fuerza.\n\n"
            "Después de años enseñando, reuní en un solo temario todo lo que realmente forma parte del proceso para desarrollar una buena estructura como trader.\n\n"
            "No es teoría ni atajos. Es un proceso completo para trabajar tu mentalidad, tu estructura y tu lectura del mercado.\n\n"
            "Y te lo digo claro: si realmente quieres aprender, empieza por aquí y comprueba por ti mismo lo que puedes desarrollar siguiendo el proceso.\n\n"
            "Aquí pueden ver todas las clases grabadas y compartir el enlace con su comunidad:\n"
            "👉 https://minedacademy.com/academy/Trading_Pro/Forex/Canal/79/220/Elliam_Herrera\n\n"
            "Compártanlo en sus grupos, porque esto puede cambiarle la visión del trading a mucha gente. 🔥\n"
            "Si ya viste alguna clase, comenta tu experiencia y ayuda a que otros también la vivan.\n\n"
            "📘 Cómo acceder al temario completo\n"
            "1️⃣ Entra a este enlace:\n"
            "👉 https://minedacademy.com/academy/Trading_Pro/Forex/Canal/79/220/Elliam_Herrera\n"
            "2️⃣ Baja un poco hasta encontrar la sección “Lista de Contenido”.\n"
            "3️⃣ Dentro de esa sección, haz clic en “Lista de Reproducción”.\n"
            "4️⃣ Ahí verás el módulo llamado “Temario”.\n"
            "5️⃣ Dentro encontrarás las 18 clases grabadas que debes ver en orden, desde la Clase 1 hasta la Clase 18, para que el proceso tenga sentido y puedas desarrollar la mentalidad y estructura completa de un trader."
        )
    }
}

# ==============================================================================
# 3. FUNCIONES DE ENVÍO
# ==============================================================================
async def enviar_aviso_sesion(app, job_data):
    tipo_session = job_data["type"]
    es_en_vivo = job_data.get("is_now", False)
    link = job_data.get("link", "")
    
    if es_en_vivo:
        mensaje = LIVE_TEMPLATES_NOW[tipo_session].format(link=link)
    else:
        if tipo_session == "BINARIAS":
            h_do, h_ar, h_pe, h_gt = job_data["horas"]
            mensaje = LIVE_TEMPLATES_PRE["BINARIAS"].format(hora_do=h_do, hora_ar=h_ar, hora_pe=h_pe, hora_gt=h_gt, link=link)
        elif tipo_session == "FOREX":
            mensaje = LIVE_TEMPLATES_PRE["FOREX"].format(link=link)
        else:
            mensaje = LIVE_TEMPLATES_PRE[tipo_session].format(link=link)
        
    try:
        await app.bot.send_message(chat_id=CHANNEL_ID, text=mensaje)
        etiqueta = "YA EN VIVO" if es_en_vivo else "PRE-AVISO -30 MIN"
        logging.info(f"Mensaje de sesión {tipo_session} ({etiqueta}) enviado exitosamente.")
    except Exception as e:
        logging.error(f"Error al enviar aviso de sesión {tipo_session}: {e}")

async def enviar_promocion(app, job_data):
    mensaje = job_data["text"]
    promo_key = job_data["key"]
    
    try:
        await app.bot.send_message(chat_id=CHANNEL_ID, text=mensaje)
        logging.info(f"Promoción ({promo_key}) enviada exitosamente.")
    except Exception as e:
        logging.error(f"Error al enviar promoción {promo_key}: {e}")

# ==============================================================================
# 4. SERVIDOR WEB FICTICIO PARA PLAN GRATUITO DE RENDER
# ==============================================================================
async def handle_ping(request):
    return web.Response(text="Bot is running OK")

async def start_dummy_server():
    port = int(os.getenv("PORT", 10000))
    app_web = web.Application()
    app_web.router.add_get("/", handle_ping)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Servidor HTTP ficticio escuchando en el puerto {port}")

# ==============================================================================
# 5. COMANDOS Y SCHEDULER
# ==============================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("¡Bienvenido, Administrador! El bot está activo con todas las promociones.")
    else:
        await update.message.reply_text("¡Hola! Soy el asistente oficial del canal. Mantente atento a los avisos.")

async def post_init(application):
    await start_dummy_server()

    for session in LIVE_SCHEDULE:
        if not session.get("active", True):
            continue

        hora_inicio = datetime.now(TIMEZONE).replace(hour=session["hour"], minute=session["minute"], second=0)
        hora_pre = hora_inicio - timedelta(minutes=30)
        
        data_pre = dict(session)
        data_pre["is_now"] = False
        scheduler.add_job(
            enviar_aviso_sesion,
            trigger='cron',
            day_of_week=session["days"],
            hour=hora_pre.hour,
            minute=hora_pre.minute,
            args=[application, data_pre]
        )

        data_now = dict(session)
        data_now["is_now"] = True
        scheduler.add_job(
            enviar_aviso_sesion,
            trigger='cron',
            day_of_week=session["days"],
            hour=session["hour"],
            minute=session["minute"],
            args=[application, data_now]
        )

    for key, item in PROMO_CONFIG.items():
        if not item.get("active", True):
            continue

        job_data = {"key": key, "text": item["text"]}
        cron_kwargs = {
            "hour": item["hour"],
            "minute": item["minute"],
            "args": [application, job_data]
        }
        if item.get("days"):
            cron_kwargs["day_of_week"] = item["days"]
        if item.get("day_of_month"):
            cron_kwargs["day"] = item["day_of_month"]

        scheduler.add_job(enviar_promocion, trigger='cron', **cron_kwargs)

    scheduler.start()
    logging.info("APScheduler iniciado correctamente.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
