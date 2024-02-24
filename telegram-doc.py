import telegram.ext
from dotenv import load_dotenv
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from telegram.ext import Updater, MessageHandler

load_dotenv()
TOKEN = os.getenv('token')


def start(update,context):
    update.message.reply_text("We are AI ACES")


def helps(update,context):
    update.message.reply_text(
        """"
        Hi. I'm your bot created by AI Aces
        Follow these : 
        1. /start - To start the bot
        2. /content - Information about AI ACES
        3. /contact - Contact us
        4. /help - If you need any help
        """
    )

def handle_document(update,context):
    document = update.message.document
    file_id = document.file_id
    file_path = context.bot.get_file(file_id)
    file_path = context.bot.get_file(file_id).download()

    update.message.reply_text(f"Thanks for sending the file :{document.file_name}")


print(TOKEN)

updater = telegram.ext.Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
dispatcher.add_handler(telegram.ext.CommandHandler('help', helps))
dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

updater.start_polling()
updater.idle()