import logging
import json
import requests
import os

from dotenv import load_dotenv
from datetime import date, time, timedelta
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
URL_DARQUBE = os.environ.get('URL_DARQUBE')
API_POLYGON = os.environ.get('API_POLYGON')

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

WATCH_LIST = {}

SPY_RATIO = 6025.99 / 600.77
ES_RATIO  = 6049.25 / 6025.99

QQQ_RATIO = 21491.31 / 522.92
NQ_RATIO = 21588.25 / 21491.31

LAST_UPDATED_AT = date.today()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def save_list():
    file = open('watch_list.json', 'w', encoding="utf8")
    json.dump(WATCH_LIST, file)


def spy_reply(spy, spx, es):
    return 'SPY: ' + format(spy, '.2f') + '\n' + 'SPX: ' + format(spx, '.2f') + '\n' + 'ES: ' + format(es, '.2f')

def qqq_reply(qqq, ndx, nq):
    return 'QQQ: ' + format(qqq, '.2f') + '\n' + 'NDX: ' + format(ndx, '.2f') + '\n' + 'NQ: ' + format(nq, '.2f')

def update_conversion_ratio(context):
    m = 'ratio updated'

    global SPY_RATIO
    global ES_RATIO

    global QQQ_RATIO
    global NQ_RATIO

    global LAST_UPDATED_AT

    try:
        spy = float(BeautifulSoup(requests.get('https://www.google.com/finance/quote/SPY:NYSEARCA').text, 'lxml').find(class_='P6K39c').text[1:].replace(',', ''))
        spx = float(BeautifulSoup(requests.get('https://www.google.com/finance/quote/.INX:INDEXSP').text, 'lxml').find(class_='P6K39c').text.replace(',', ''))
        es = float(BeautifulSoup(requests.get('https://www.google.com/finance/quote/ESW00:CME_EMINIS').text, 'lxml').find(class_='P6K39c').text[1:].replace(',', ''))

        qqq = float(BeautifulSoup(requests.get('https://www.google.com/finance/quote/QQQ:NASDAQ').text, 'lxml').find(class_='P6K39c').text[1:].replace(',', ''))
        ndx = float(BeautifulSoup(requests.get('https://www.google.com/finance/quote/NDX:INDEXNASDAQ').text, 'lxml').find(class_='P6K39c').text.replace(',', ''))
        nq = float(BeautifulSoup(requests.get('https://www.google.com/finance/quote/NQW00:CME_EMINIS').text, 'lxml').find(class_='P6K39c').text[1:].replace(',', ''))

        SPY_RATIO = spx / spy
        ES_RATIO = es / spx

        QQQ_RATIO = ndx / qqq
        NQ_RATIO = nq / ndx

        LAST_UPDATED_AT = date.today()
        print(LAST_UPDATED_AT)
    except:
        m = 'failed to update ratio'

    print(m)
    

async def spy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    spy = float(update.message.text.split()[1])
    spx = spy * SPY_RATIO
    es = spx * ES_RATIO

    reply = spy_reply(spy, spx, es)

    await update.message.reply_text(reply)

async def spx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    spx = float(update.message.text.split()[1])
    spy = spx / SPY_RATIO
    es = spx * ES_RATIO

    reply = spy_reply(spy, spx, es)

    await update.message.reply_text(reply)

async def es_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    es = float(update.message.text.split()[1])
    spx = es / ES_RATIO
    spy = spx / SPY_RATIO

    reply = spy_reply(spy, spx, es)

    await update.message.reply_text(reply)


async def qqq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    qqq = float(update.message.text.split()[1])
    ndx = qqq * QQQ_RATIO
    nq = ndx * NQ_RATIO

    reply = qqq_reply(qqq, ndx, nq)

    await update.message.reply_text(reply)

async def ndx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    qqq = float(update.message.text.split()[1])
    ndx = qqq * QQQ_RATIO
    nq = ndx * NQ_RATIO

    reply = qqq_reply(qqq, ndx, nq)

    await update.message.reply_text(reply)

async def nq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nq = float(update.message.text.split()[1])
    ndx = nq / NQ_RATIO
    qqq = ndx / QQQ_RATIO

    reply = qqq_reply(qqq, ndx, nq)

    await update.message.reply_text(reply)


async def vix_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply = ''
    try:

        request = requests.get('https://www.cnbc.com/quotes/@VX.1', headers=HEADERS)
        soup = BeautifulSoup(request.text, 'lxml')
        date = soup.find(class_='Summary-data Summary-future').find_all(name='li')[-3].find(class_="Summary-value").text
        vx_1 = soup.find(class_='QuoteStrip-lastPrice').text
        reply += 'VX.1:  ' + vx_1 + '  到期日：' + date + '\n'

        request = requests.get('https://www.cnbc.com/quotes/@VX.2', headers=HEADERS)
        vx_2 = BeautifulSoup(request.text, 'lxml').find(class_='QuoteStrip-lastPrice').text
        reply += 'VX.2:  ' + vx_2 + '\n'

        request = requests.get('https://www.cnbc.com/quotes/VIX', headers=HEADERS)
        vix1m = BeautifulSoup(request.text, 'lxml').find(class_='QuoteStrip-lastPrice').text
        reply += 'VIX:    ' + vix1m + '\n'

        request = requests.get('https://www.cnbc.com/quotes/VIX3M', headers=HEADERS)
        vix3m = BeautifulSoup(request.text, 'lxml').find(class_='QuoteStrip-lastPrice').text
        reply += 'VIX3M: ' + vix3m + '\n'

        reply += '注意：临近下一到期日两周以内的时候，请结合参考VX.1和VX.2的价格（通常在到期前一周左右会切换至下一合约）'
                
    except:
        reply += '\nerror occurred'


    await update.message.reply_text(reply)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply = '@seartch_zeta_bot 想要搜索的内容  ：搜索群内聊天记录' + '\n'
    reply += '/vix  ：vix速查' + '\n'
    reply += '/list  ：查看群友荐股列表' + '\n'
    reply += '/add NVDA 128抄底  ：添加NVDA至列表' + '\n'
    reply += '/remove NVDA  ：从列表中移除NVDA' + '\n'
    reply += '/qqq /ndx /nq /spy /spx /es  ：指数ETF期货数值互换，空格后加上数值' + '\n\n'
    reply += '使用时请注意格式和空格~'

    await update.message.reply_text(reply)


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply = '***赌财报风险极高，谨慎跟单，盈亏自负！***\n'
    try:
        for k, v in WATCH_LIST.items():
            price = ''
            try:
                price = str(requests.get(URL_DARQUBE.format(k)).json()['price']) + ', '
            except:
                price = ''
            reply += k + ': ' + price + v + '\n'
        
        # reply += '\n' + '公用notion笔记: https://www.notion.so/invite/f4bd299b55403cc58da5ab4ddd31969057ec53ea'
    except:
      reply = 'error' 

    await update.message.reply_text(reply)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    reply = ''
    try:
        content = update.message.text.split()
        ticker = content[1].upper()
        note = ''.join(content[2:])

        if ticker in WATCH_LIST:
            reply = ticker + ' updated'
        else:
            reply = ticker + ' added to watchlist'
            
        WATCH_LIST[ticker] = note
    except:
        reply = 'error'

    save_list()
    
    await update.message.reply_text(reply)


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    reply = ''
    try:
        ticker = update.message.text.split()[1].upper()
        del WATCH_LIST[ticker]

        reply = ticker + ' removed'

    except:
        reply = 'error'

    save_list()

    await update.message.reply_text(reply)

# async def quick_financials_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     url = URL_QUOTE.format(update.message.text[7:])
#     js = json.loads(requests.get(url).text)
#     await update.message.reply_text(js['price'])

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('last updated at: ' + LAST_UPDATED_AT.strftime('%Y-%m-%d'))

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update_conversion_ratio(None)
    await update.message.reply_text('ratio updated')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    application.job_queue.run_daily(update_conversion_ratio, time(12, 0, 0, 0), days=(1, 2, 3, 4, 5))

    # application.add_handler(CommandHandler("quick_financials", quick_financials_command))
    application.add_handler(CommandHandler("vix", vix_command))

    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("remove", remove_command))

    application.add_handler(CommandHandler("spy", spy_command))
    application.add_handler(CommandHandler("spx", spx_command))
    application.add_handler(CommandHandler("es", es_command))

    application.add_handler(CommandHandler("qqq", qqq_command))
    application.add_handler(CommandHandler("ndx", ndx_command))
    application.add_handler(CommandHandler("nq", nq_command))

    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("update", update_command))




    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":

    WATCH_LIST = json.load(open('watch_list.json', 'r', encoding="utf8"))
    update_conversion_ratio(None)

    main()