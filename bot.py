import os
import logging
import random
import threading
import http.server
import socketserver
from groq import Groq
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ContextTypes
)

# 1. SERVIDOR WEB MINIMALISTA (Para que Render Free no se apague)
def start_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Servidor de mantenimiento en puerto {port}")
        httpd.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# 2. CONFIGURACIÓN DE LOGS Y CLIENTES
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("Faltan las variables de entorno TELEGRAM_TOKEN o GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

SISTEMA_MISTICO = (
    "Eres un guía místico y experto en energías cósmicas. "
    "Respondes de forma breve, sabia y con muchos emojis ✨🔮🌙."
)

# --- FUNCIONES DEL BOT ---

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Bienvido al Oráculo Digital. ✨\n\n"
        "Puedes hablarme normalmente o usar /jugar para ver la interfaz mística."
    )

# Interfaz Gráfica (Botones)
async def menu_juego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔮 Tarot", callback_data='tarot'),
            InlineKeyboardButton("✨ Horóscopo", callback_data='horoscopo')
        ],
        [
            InlineKeyboardButton("🎲 Número de la Suerte", callback_data='suerte'),
            InlineKeyboardButton("🪐 Energía Hoy", callback_data='energia')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ Selecciona una opción del plano astral:", reply_markup=reply_markup)

# Manejador de clics en botones
async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    opcion = query.data
    prompt = f"El usuario eligió {opcion}. Dame una predicción o consejo místico muy breve."
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": SISTEMA_MISTICO}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        await query.edit_message_text(text=f"✨ {completion.choices[0].message.content}")
    except Exception as e:
        await query.edit_message_text(text="✨ Las estrellas están nubladas... intenta luego.")

# Chat normal con IA
async def hablar_con_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": SISTEMA_MISTICO}, {"role": "user", "content": update.message.text}],
            model="llama-3.3-70b-versatile",
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text("✨ Hubo una interferencia cósmica.")

# --- INICIO DEL BOT ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('jugar', menu_juego))
    
    # Manejador de botones
    app.add_handler(CallbackQueryHandler(manejar_botones))
    
    # Manejador de texto (IA)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), hablar_con_ia))

    print("🔮 Bot 2026 listo y conectado...")
    app.run_polling()