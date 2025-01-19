import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    CallbackContext,
)
import os
from dotenv import load_dotenv
from enum import IntEnum

# load env vars
load_dotenv()

# Get the token for the bot
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Possible states in the registration and login
class AuthState(IntEnum):
    REGISTRATION_USERNAME = 1
    REGISTRATION_PASSWORD = 2
    LOGIN_USERNAME = 3
    LOGIN_PASSWORD = 4


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /start command
    :param update:
    :param context:
    :return:
    """
    welcome_message = (
        "Welcome to the weather bot!\n\n"
        "Send a city name and I will tell you the weather there\n\n"
        ""
        "For example try: Berlin"
    )

    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /help command
    :param update:
    :param context:
    :return:
    """
    help_message = (
        "Bot Commands:\n\n"
        "/start - Start the bot\n"
        "/register - Register in the app\n"
        "/help - Shows help\n\n"
        "To get the weather information, type in the name of the city!"
    )

    await update.message.reply_text(help_message)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Let's register you in the app.\nPlease enter username:"
    )
    return AuthState.REGISTRATION_USERNAME


async def handle_registration_username(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    username = update.message.text.strip()

    context.user_data["username"] = username

    password_prompt = "Please enter a password: "

    await update.message.reply_text(password_prompt)
    return AuthState.REGISTRATION_PASSWORD


async def handle_registration_password(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    password = update.message.text

    await update.message.delete()

    username = context.user_data["username"]

    from what_weather.auth import register_user

    success, message = register_user(username, password)

    context.user_data.clear()

    if success:
        await update.message.reply_text(f"Thank you for registering, {username}.")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"Registration failed: {message}")
        return ConversationHandler.END


async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's log you in.\nPlease enter username:")
    return AuthState.LOGIN_USERNAME


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the messages containing a city
    :param update:
    :param context:
    :return:
    """
    city = update.message.text.lower()
    # here goes the api call (Implementing authentication)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the message text

    await update.message.reply_text(update.message.text)


async def create_bot():
    """
    Main function to run the bot. This function handles the complete lifecycle
    of the bot, from initialization to shutdown.
    """
    # Create the bot application instance using the token
    bot_app = None
    # Initialize the bot application
    bot_app = Application.builder().token(TOKEN).build()

    # Registration conversation handler
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("register", start_registration)],
        states={
            AuthState.REGISTRATION_USERNAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_registration_username
                )
            ],
            AuthState.REGISTRATION_PASSWORD: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_registration_password
                )
            ],
        },
        fallbacks=[],
    )

    # Add command handlers
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(registration_handler)
    bot_app.add_handler(CommandHandler("login", start_login))

    # pass webhook settings to teleg
    await bot_app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/telegram", allowed_updates=Update.ALL_TYPES
    )

    async with bot_app:
        await bot_app.start()
        await bot_app.run_webhook(
            webhook_url=WEBHOOK_URL,
            cert="/app/certs/cert.pem",
            key="/app/certs/key.pem",
            drop_pending_updates=True,
        )
        await bot_app.stop()


if __name__ == "__main__":
    asyncio.run(create_bot())
