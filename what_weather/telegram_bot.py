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


# Possible states in the registration and login
class AuthState(IntEnum):
    CHOOSING_USERNAME = 1
    CHOOSING_PASSWORD = 2

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
        "/help - Shows help\n\n"
        "To get the weather information, type in the name of the city!"
    )

    await update.message.reply_text(help_message)




async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_registation_message = (
        "Let's register you in the app.\n"
        "Please enter username: "
    )
    await update.message.reply_text(start_registation_message)
    return AuthState.CHOOSING_USERNAME


async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_login_message = (
        "Let's log you in.\n"
        "Please enter username: "
    )

    username = update.message.text

    # Store username in context to be used later
    context.user_data["username"] = username

    await update.message.reply_text(start_login_message)

    return AuthState.CHOOSING_USERNAME

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_username_message = (
        "Please enter password: "
    )

    username = context.user_data["username"]
    password = update.message.text

    # Delete message containing password for security
    await update.message.delete()




    await update.message.reply_text(handle_username_message)
    return AuthState.CHOOSING_PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handle_password_message = (
        "Please enter password: "
    )
    await update.message.reply_text(handle_password_message)
    return AuthState.CHOOSING_PASSWORD

async def cancel_registration

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the messages containing a city
    :param update:
    :param context:
    :return:
    """
    city = update.message.text.lower()
    # here goes the api call (Implementing authentication)


def main():
    """
    Main function to run the bot
    :return:
    """
    # Create the bot applicatino instance using the token
    bot_app = Application.builder().token(TOKEN).build()

    # Add command handlers
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("registration", start_registration))
    bot_app.add_handler(CommandHandler("login", start_login))
    # Add message handler
    # here should be a handler for dealing with the queries but for now I don't have it done.

    # bot polling searching for messages
    bot_app.run_polling(poll_interval=5)

if __name__ == "__main__":
    main()


