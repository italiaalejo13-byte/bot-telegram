print("EL ARCHIVO SE EJECUTA")

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import json
import os
import requests

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN no encontrado")
    
# 👉 IDs de administradores (pon tu ID)
ADMINS = [7131555659, 8495130818]

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
        "/saludo\n"
        "/bin <bin_number>"
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

# ---------- Consultar BIN ----------
async def bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        bin_number = context.args[0]  # Obtener el primer argumento después del comando
        url = f'https://binlist.net/{bin_number}'
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                respuesta = (
                    f"Información del BIN {bin_number}:\n"
                    f"💳 Banco: {data.get('bank', {}).get('name', 'No disponible')}\n"
                    f"🌍 País: {data.get('country', {}).get('name', 'No disponible')}\n"
                    f"🏦 Tipo de tarjeta: {data.get('type', 'No disponible')}\n"
                    f"💳 Marca: {data.get('scheme', 'No disponible')}"
                )
                await update.message.reply_text(respuesta)
            else:
                await update.message.reply_text(f"⚠️ No se encontró información para el BIN {bin_number}.")
        except requests.RequestException as e:
            await update.message.reply_text("Error al conectar con la API de Binlist.")
    else:
        await update.message.reply_text("❗ Debes proporcionar un número de BIN después del comando. Ejemplo: `/bin 411111`")

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
    except (IndexError, ValueError):
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
    app.add_handler(CommandHandler("bin", bin))

    app.run_polling()

if __name__ == "__main__":
    main()