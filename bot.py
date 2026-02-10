import logging
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes



# 1. Configuración de registros para ver qué pasa en la consola
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
import os
import logging
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- ESTO ES LO QUE PEGAS ARRIBA ---
# El código buscará estas variables en el sistema operativo
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validación (para que el bot te avise si faltan las llaves)
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    print("❌ ERROR: No se encontraron las variables de entorno.")
    print("Asegúrate de configurarlas en el panel de control de tu hosting.")
# ----------------------------------

client = Groq(api_key=GROQ_API_KEY)

# Instrucciones de personalidad
SISTEMA_MISTICO = (
    "Eres un guía holístico y espiritual experto en astrología y energías cósmicas. "
    "Tus respuestas son místicas, sabias, pero breves y directas. "
    "Siempre incluyes emojis como ✨, 🔮, 🪐 o 🌙. Responde siempre en español."
)

# --- FUNCIONES DEL BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ El cosmos te saluda. ✨\n\n"
        "Soy tu conexión con la sabiduría universal procesada por Groq.\n"
        "Hazme una pregunta sobre tu destino o pide un consejo energético."
    )

async def responder_con_groq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Efecto de "Escribiendo..." en Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Llamada a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SISTEMA_MISTICO},
                {"role": "user", "content": update.message.text}
            ],
            model="llama-3.3-70b-versatile", # El modelo más potente disponible en Groq
            temperature=0.7, # Un toque de creatividad mística
        )
        
        respuesta = chat_completion.choices[0].message.content
        await update.message.reply_text(respuesta)

    except Exception as e:
        print(f"Error en Groq: {e}")
        await update.message.reply_text("✨ Las interferencias astrales son fuertes. Reintenta en un momento.")

# --- INICIO ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder_con_groq))

    print("🔮 Oráculo Groq iniciado y esperando señales del universo...")
    app.run_polling()