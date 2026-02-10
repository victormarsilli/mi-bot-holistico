import os
import logging
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

# =========================================================
# 1. SERVIDOR WEB PARA MANTENER VIVO EL BOT (RENDER FREE)
# =========================================================
def start_server():
    # Render asigna automáticamente un puerto en la variable PORT
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    
    # Esto crea un servidor básico que responde "OK" a las peticiones de Render
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌍 Servidor de mantenimiento activo en el puerto: {port}")
        httpd.serve_forever()

# Iniciamos el servidor en un hilo aparte para que no bloquee al bot
threading.Thread(target=start_server, daemon=True).start()

# =========================================================
# 2. CONFIGURACIÓN DEL BOT Y LA IA
# =========================================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("❌ Faltan llaves en las variables de entorno.")

client = Groq(api_key=GROQ_API_KEY)

SISTEMA_MISTICO = (
    "Eres un guía místico experto en el cosmos. Respondes de forma breve, "
    "usando metáforas estelares y muchos emojis ✨🔮🌙."
)

# --- FUNCIONES DEL ORÁCULO ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    bienvenida = (
        f"✨ ¡Hola, {user_name}! Bienvenido al **Oráculo Digital** ✨\n\n"
        "Soy tu conexión con el cosmos. Aquí tienes cómo usarme:\n\n"
        "💬 **Conversar:** Escríbeme y te responderé con sabiduría.\n"
        "🎮 **Interfaz:** Usa /jugar para abrir el panel de botones.\n"
        "❓ **Ayuda:** Usa /ayuda para más info."
    )
    await update.message.reply_text(bienvenida, parse_mode='Markdown')

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 **Guía de Consulta** 🌟\n\n"
        "• Puedes hablarme libremente.\n"
        "• Los botones de /jugar son interactivos.\n"
        "• El servidor está sincronizado con el cosmos (y con Render).",
        parse_mode='Markdown'
    )

async def menu_juego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 Futuro", callback_data='futuro'), 
         InlineKeyboardButton("✨ Energía", callback_data='energia')],
        [InlineKeyboardButton("🌙 Consejo", callback_data='consejo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ Elige tu destino:", reply_markup=reply_markup)

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    prompt = f"El usuario eligió la opción {query.data}. Dame un consejo místico breve."
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": SISTEMA_MISTICO}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        await query.edit_message_text(text=f"✨ {completion.choices[0].message.content}")
    except Exception:
        await query.edit_message_text(text="✨ Conexión estelar interrumpida.")

async def hablar_con_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": SISTEMA_MISTICO}, {"role": "user", "content": update.message.text}],
            model="llama-3.3-70b-versatile",
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception:
        await update.message.reply_text("✨ Las estrellas están nubladas hoy.")

# --- INICIO ---


    
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # 1. Comandos primero
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ayuda', ayuda))
    app.add_handler(CommandHandler('jugar', menu_juego))
    
    # 2. Manejador de botones (¡ESTE ES EL QUE HACE QUE FUNCIONE EL CLIC!)
    app.add_handler(CallbackQueryHandler(manejar_botones))
    
    # 3. Chat normal al final
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), hablar_con_ia))

    app.run_polling()