
import logging
import threading
from vesna.wfdatabase import WFDatabase
from vesna.telegram import WFVesnaTelegram
from vesna.googleparser import VesnaParser, DetainedInfo


dbUrl = "data/vesnabot.sqlite"
telegramToken = "put your key here"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    print("Bot started")
    wftg = WFVesnaTelegram(dbUrl, telegramToken)
    wftg.run()


    wftg.idle()

# Run main() method
if __name__ == '__main__':
    main()
