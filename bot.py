print("EL ARCHIVO SE EJECUTA")

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import json
import os

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN no encontrado")
    
# 👉 IDs de administradores (pon tu ID)
ADMINS = [7131555659]

DATA_FILE = "datos.json"

# ---------- DATOS ----------
def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def obtener_saldo(user_id):
    datos = cargar_datos()
    return datos.get(str(user_id), 0)

def sumar_saldo(user_id, cantidad):
    datos = cargar_datos()
    uid = str(user_id)
    datos[uid] = datos.get(uid, 0) + cantidad
    guardar_datos(datos)

# ---------- COMANDOS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot encendido!\n\n"
        "/saldo\n"
        "/dado\n"
        "/saludo"
    )

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    saldo = obtener_saldo(user_id)
    await update.message.reply_text(f"💰 Tu saldo real es: ${saldo}")

async def dado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    numero = random.randint(1, 6)
    sumar_saldo(user_id, numero)
    await update.message.reply_text(
        f"🎲 Salió {numero}\n"
        f"💰 Se sumó a tu saldo"
    )

async def saludo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    saludos = [
        "👋 Hola!",
        "😄 Qué tal!",
        "🔥 Bienvenido!",
        "🚀 Vamos con todo!",
        "😎 Todo bien?"
    ]
    await update.message.reply_text(random.choice(saludos))

# ---------- SOLO ADMINS ----------
async def add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("⛔ No eres admin")
        return

    try:
        user_id = int(context.args[0])
        cantidad = int(context.args[1])
        sumar_saldo(user_id, cantidad)
        await update.message.reply_text("✅ Saldo agregado")
    except:
        await update.message.reply_text("Uso: /addsaldo user_id cantidad")

# ---------- MAIN ----------
def main():
    print("Bot encendido 🚀")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("dado", dado))
    app.add_handler(CommandHandler("saludo", saludo))
    app.add_handler(CommandHandler("addsaldo", add_saldo))

    app.run_polling()

if __name__ == "__main__":
    main()
