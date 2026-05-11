import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8797541775:AAGen_koRkUZ-ikn5QSnYVgNZefx9iacmak"

# --- API FUNCTIONS ---

def nobitex(symbol):
    url = f"https://api.nobitex.ir/market/stats?srcCurrency={symbol}&dstCurrency=rls"
    r = requests.get(url).json()
    return float(r["stats"][f"{symbol}-rls"]["bestSell"])

def wallex(symbol):
    url = "https://api.wallex.ir/v1/markets"
    r = requests.get(url).json()
    for m in r["result"]["symbols"]:
        if m["symbol"] == f"{symbol}IRT":
            return float(m["stats"]["ask"])
    return 0

def ramzinex(symbol):
    url = "https://api.ramzinex.com/exchange/api/v1.0/exchange/pairs"
    r = requests.get(url).json()
    for p in r["data"]:
        if p["symbol"] == f"{symbol}_IRT":
            return float(p["sell"])
    return 0

def tabdeal(symbol):
    url = "https://api.tabdeal.org/api/v1/market/tickers"
    r = requests.get(url).json()
    for t in r["result"]:
        if t["symbol"] == f"{symbol}-IRT":
            return float(t["ask"])
    return 0

# --- ARBITRAGE LOGIC ---

def find_best():
    symbols = ["TRX", "XRP", "DOGE", "MATIC", "ADA"]
    best = {"profit": -999999}

    for s in symbols:
        prices = {
            "nobitex": nobitex(s),
            "wallex": wallex(s),
            "ramzinex": ramzinex(s),
            "tabdeal": tabdeal(s)
        }

        for buy in prices:
            for sell in prices:
                if buy != sell:
                    profit = prices[sell] - prices[buy]
                    if profit > best["profit"]:
                        best = {
                            "symbol": s,
                            "buy": buy,
                            "sell": sell,
                            "profit": int(profit)
                        }

    return best

# --- TELEGRAM BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات آربیتراژ فعال شد.\nهر ۵ ثانیه بهترین فرصت را ارسال می‌کنم.")

    while True:
        best = find_best()
        msg = (
            f"🔥 فرصت آربیتراژ\n"
            f"ارز: {best['symbol']}\n"
            f"خرید از: {best['buy']}\n"
            f"فروش در: {best['sell']}\n"
            f"سود: {best['profit']} تومان"
        )
        await update.message.reply_text(msg)
        time.sleep(5)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
