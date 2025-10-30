"""
Script temporal para obtener el Chat ID de tus grupos de Telegram.
Ejecuta este script después de configurar TELEGRAM_API_ID, TELEGRAM_API_HASH y TELEGRAM_PHONE en .env
"""

import asyncio
from telethon import TelegramClient
import config

async def list_chats():
    """Lista todos tus chats y muestra sus IDs."""
    print("Conectando a Telegram...\n")

    client = TelegramClient(
        'temp_session',
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH
    )

    await client.start(phone=config.TELEGRAM_PHONE)

    print("="*70)
    print("TUS CHATS Y GRUPOS:")
    print("="*70)

    async for dialog in client.iter_dialogs():
        # Solo mostrar grupos y canales (no chats individuales)
        if dialog.is_group or dialog.is_channel:
            chat_id = dialog.id
            # Convertir a formato con prefijo -100 si es necesario
            if not str(chat_id).startswith('-100'):
                chat_id = int('-100' + str(abs(chat_id)))

            print(f"\nNombre: {dialog.name}")
            print(f"Chat ID: {chat_id}")
            print(f"Tipo: {'Canal' if dialog.is_channel else 'Grupo'}")
            print("-"*70)

    print("\n" + "="*70)
    print("Copia el Chat ID del grupo que quieres monitorizar")
    print("y pégalo en tu archivo .env como:")
    print("TELEGRAM_CHAT_ID=-1001234567890")
    print("="*70 + "\n")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(list_chats())
