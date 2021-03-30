import logging
import threading
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from vesna.googleparser import DetainedInfo, VesnaParser
from vesna.wfdatabase import WFDatabase
from time import sleep
import telegram

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
URL, CSVFILE = range(2)

messageTemplate = """
Совпадение:
Весна: {nameVesna}
WF: {nameWF}
---
Город: {city}
Где находится: {place}
Коментарии: {comments}
"""

class WFVesnaTelegram:
    chatId = 0
    dbUrl = None
    tgToken = None
    bot = None
    backgroungThread = None
    urlToMonitor = None

    def __init__(self, dbUrl, tgToken):
        self.dbUrl = dbUrl
        self.tgToken = tgToken
        self.bot = telegram.Bot(token=tgToken)

    def run(self):
        updater = Updater(self.tgToken, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("reset", self.reset))
        dp.add_handler(self.newUrlHandler)
        updater.start_polling()

    def start(self, update, context):
        self.chatId = update.message.chat_id
        update.message.reply_text('Roger that! ' + str(update.message.chat_id))
        if "urlToMonitor" not in context.user_data:
            update.message.reply_text('URL to monitor is not defined! Run /url command to define monitoring URL')
            return
        self.urlToMonitor = context.user_data["urlToMonitor"]
        if not self.backgroungThread or not self.backgroungThread.isAlive():
            self.backgroungThread = threading.Thread(target=self.backgroundCheck, args=())
            self.backgroungThread.daemon = True
            self.backgroungThread.start()
            update.message.reply_text('Background check started: '+self.urlToMonitor)

    def help(self, update, context):
        update.message.reply_text('Supported commands: /url')

    def reset(self, update, context):
        wfdb = WFDatabase(self.dbUrl)
        wfdb.resetState()
        update.message.reply_text('Reset DB state')

    def ask_for_monitoring_url(update, context):
        update.message.reply_text('Please enter URL to monitor')
        return URL

    def add_monitoring_url(update, context):
        update.message.reply_text('Monitoring URL is updated: ' + update.message.text)
        context.user_data["urlToMonitor"] = update.message.text
        return ConversationHandler.END

    def cancel(update, context):
        update.message.reply_text('Operation cancelled')
        return ConversationHandler.END

    newUrlHandler = ConversationHandler(
        entry_points=[CommandHandler('url', ask_for_monitoring_url)],
        states={
            URL: [MessageHandler(Filters.regex('^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;=.]+$'), add_monitoring_url)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    def sendNotification(self, detained: DetainedInfo):
        self.bot.sendMessage(chat_id=self.chatId, text=messageTemplate.format(
            nameVesna=detained.name,
            nameWF=detained.wfName,
            city=detained.citi,
            place=detained.place,
            comments=detained.comments
        ))

    def idle(self):
        while True:
            sleep

    def backgroundCheck(self):
        parser = VesnaParser()
        wfdb = WFDatabase(self.dbUrl)
        while True:
            logger.info("Check URL: "+self.urlToMonitor)
            detainedList = parser.parseTalbe(self.urlToMonitor)
            matchedList = wfdb.findOverlap(detainedList)
            if matchedList:
                for match in matchedList:
                    logger.info(match.wfName)
                    self.sendNotification(match)
                    wfdb.markDetained(match)
            logger.info("Sleep 30 seconds")
            time.sleep(30)


