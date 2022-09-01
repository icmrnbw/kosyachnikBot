import logging
import os

from telegram.ext import ApplicationBuilder, CommandHandler

from handlers.info import info
from handlers.kosyachnik import kosyachnik
from handlers.register import register
from handlers.stats import stats

PORT = int(os.environ.get('PORT', '8443'))
TOKEN = '5715448930:AAGbnJDgHJElbYVYEhR1f7yKTpB7jkZ8FhI'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()  # this code creates our application using token of our bot
    handlers = [  # setting handlers for our bot
        CommandHandler('info', info),
        CommandHandler('register', register),
        CommandHandler('kosyachnik', kosyachnik),
        CommandHandler('stats', stats)
    ]

    application.add_handlers(handlers)  # adding handlers

    # application.run_polling()  # we use polling in case we want to test it by running it on our PC

    application.run_webhook(  # adding webhooks only if the bot is run on a hosting
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url='https://kosyachnik-bot.herokuapp.com/' + TOKEN
    )
