from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import time
import asyncio

TOKEN = "8561778753:AAH67ygxhEwsmxtrll9WkDaN2BX0sCD-lzo"

suscriptores = []

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu bot 🤖\n\n"
        "Comandos disponibles:\n"
        "/start - Iniciar\n"
        "/ayuda - Ayuda\n"
        "/suscribir - Recibir notificaciones\n"
        "/info - Información\n"
        "/reglas - Ver reglas del grupo\n"
        "/contacto - Contacto"
    )

# /ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Puedo ayudarte con:\n"
        "- Responder preguntas frecuentes\n"
        "- Moderar el grupo\n"
        "- Enviarte notificaciones\n\n"
        "Escríbeme cualquier pregunta."
    )

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Este bot fue creado para gestionar y moderar el grupo.")

# /reglas
async def reglas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Reglas del grupo:\n"
        "1. Sé respetuoso\n"
        "2. No spam\n"
        "3. No contenido inapropiado\n"
        "4. Sigue las instrucciones del admin"
    )

# /contacto
async def contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Contáctanos en: @tu_usuario")

# /suscribir
async def suscribir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in suscriptores:
        suscriptores.append(user_id)
        await update.message.reply_text("✅ Suscrito a notificaciones.")
    else:
        await update.message.reply_text("Ya estás suscrito.")

# /notificar (solo admins)
async def notificar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = " ".join(context.args)
    if not mensaje:
        await update.message.reply_text("Uso: /notificar Tu mensaje aquí")
        return
    for user_id in suscriptores:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"🔔 Notificación:\n{mensaje}")
        except:
            pass
    await update.message.reply_text(f"✅ Notificación enviada a {len(suscriptores)} usuarios.")

# /ban (solo admins)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🚫 {user.first_name} fue baneado.")
    else:
        await update.message.reply_text("Responde al mensaje de un usuario para banearlo.")

# /mute (solo admins)
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.effective_chat.id, user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(f"🔇 {user.first_name} fue silenciado.")
    else:
        await update.message.reply_text("Responde al mensaje de un usuario para silenciarlo.")

# Respuestas automáticas
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if "hola" in texto:
        await update.message.reply_text("¡Hola! 👋 ¿En qué puedo ayudarte?")
    elif "precio" in texto:
        await update.message.reply_text("💰 Para precios escribe /contacto")
    elif "gracias" in texto:
        await update.message.reply_text("¡De nada! 😊")
    elif "horario" in texto:
        await update.message.reply_text("🕐 Estamos disponibles 24/7")

# Iniciar
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ayuda", ayuda))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("reglas", reglas))
app.add_handler(CommandHandler("contacto", contacto))
app.add_handler(CommandHandler("suscribir", suscribir))
app.add_handler(CommandHandler("notificar", notificar))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("Bot corriendo...")
app.run_polling()