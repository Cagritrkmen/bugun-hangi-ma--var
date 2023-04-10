import datetime
import pytz
import telegram
from telegram.ext import CommandHandler, Updater

import requests

url = "URL"

tz = pytz.timezone('Europe/Istanbul')

headers = {
    "x-rapidapi-host": "HOST",
    "x-rapidapi-key": "APİ-KEY"
}

def start(update, context):
    update.message.reply_text('Merhaba! Maçları öğrenmek için /maclar komutunu kullanabilirsiniz.')

def maclar(update, context):
    now = datetime.datetime.now(tz)
    date_string = now.strftime("%Y-%m-%d")

    params = {
        "league": "203",  #superlig
        "season": "2022",
        "date": date_string
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        fixtures = response.json()["response"]
        message = "Bugünkü Maçlar:\n\n"
        for fixture in fixtures:
            home_team = fixture["teams"]["home"]["name"]
            away_team = fixture["teams"]["away"]["name"]
            
            kickoff_time = fixture["fixture"]["date"]
            utc_time = datetime.datetime.fromisoformat(kickoff_time)
            localized_time = utc_time.astimezone(tz)
            kickoff_time = localized_time.strftime("%H:%M")
            
            message += f"{home_team} vs {away_team} - Başlama saati: {kickoff_time}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("API'ye erişilemedi.")

def main():
    updater = Updater("TELEGRAM TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("maclar", maclar))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
