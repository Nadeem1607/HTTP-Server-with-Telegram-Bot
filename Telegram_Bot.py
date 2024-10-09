import os
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Dictionary to store user-specific IP and port
user_connections = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please provide the server IP and port in the format: `ip:port`")

async def set_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    input_text = update.message.text

    # Split the input into IP and port
    try:
        ip, port = input_text.split(':')
        port = int(port)

        # Validate IP and port
        if not (0 <= port <= 65535):
            await update.message.reply_text("Port must be between 0 and 65535.")
            return

        # Store the connection info
        user_connections[user_id] = (ip, port)
        await update.message.reply_text(f"Connection set to {ip}:{port}. You can now use /fetch to retrieve data.")
    except ValueError:
        await update.message.reply_text("Invalid format. Please use `ip:port`.")

async def fetch_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check if the user has set a connection
    if user_id not in user_connections:
        await update.message.reply_text("Please set the connection first using /setconnection.")
        return

    ip, port = user_connections[user_id]

    # Attempt to connect to the server
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{ip}:{port}/api/data') as response:
                data = await response.json()
                await update.message.reply_text(f"Data from server: {data}")
    except Exception as e:
        await update.message.reply_text(f"Failed to connect to {ip}:{port}. Error: {str(e)}")

def main():
    application = ApplicationBuilder().token('<Your_Bot_Token>').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setconnection", set_connection))
    application.add_handler(CommandHandler("fetch", fetch_data))

    # Allow users to send IP and port directly
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_connection))


    application.run_polling()

if __name__ == '__main__':
    main()
