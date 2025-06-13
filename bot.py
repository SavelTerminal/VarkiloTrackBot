import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from supabase import create_client, Client
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)

# --- ENV Variabili ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Connessioni ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- /start ---
@dp.message(commands=['start'])
async def start(message: Message):
    await message.answer("👋 Benvenuto! Inviami /addwallet per registrare un wallet da tracciare.")

# --- /addwallet ---
@dp.message(commands=['addwallet'])
async def add_wallet_command(message: Message):
    await message.answer("✏️ Invia l'indirizzo del wallet seguito da uno spazio e il nome personalizzato.\nEsempio:\n`9zxo...xd3w Italianrot wallet`", parse_mode="Markdown")

@dp.message()
async def handle_wallet_input(message: Message):
    text = message.text.strip()
    parts = text.split(" ")

    if len(parts) < 2:
        await message.answer("❌ Formato non valido. Devi inviare: `wallet_address nome_wallet`", parse_mode="Markdown")
        return

    wallet_address = parts[0]
    wallet_name = " ".join(parts[1:])
    user_id = str(message.from_user.id)

    # Check se già esiste
    existing = supabase.table("wallets").select("*").eq("user_id", user_id).eq("wallet", wallet_address).execute()

    if existing.data:
        await message.answer("⚠️ Questo wallet è già stato salvato.")
        return

    # Inserimento su Supabase
    result = supabase.table("wallets").insert({
        "user_id": user_id,
        "wallet": wallet_address,
        "wallet_name": wallet_name,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    if result.data:
        await message.answer(f"✅ Wallet salvato con successo!\nNome: {wallet_name}\nAddress: `{wallet_address}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Errore nel salvataggio, riprova.")

# --- Avvio ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
