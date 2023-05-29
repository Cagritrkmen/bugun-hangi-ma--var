import datetime
import pytz
import telegram
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import requests

url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
standings_url = "https://api-football-v1.p.rapidapi.com/v3/standings"

tz = pytz.timezone('Europe/Istanbul')

headers = {
    "x-rapidapi-host": "HOST",
    "x-rapidapi-key": "APİ_KEY"
}

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Maçlar", callback_data='matches')],
        [InlineKeyboardButton("Puan Durumu", callback_data='standings')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text='Merhaba! Ne yapmak istersiniz?', reply_markup=reply_markup)

def matches(update, context):
    now = datetime.datetime.now(tz)
    date_string = now.strftime("%Y-%m-%d")

    super_params = {
        "league": "203",
        "season": "2022",
        "date": date_string
    }
    premier_params = {
        "league": "39",
        "season": "2022",
        "date": date_string
    }
    champions_params = {
        "league": "2",
        "season": "2022",
        "date": date_string
    }
    champions_response = requests.get(url, headers=headers, params=champions_params)
    premier_response = requests.get(url, headers=headers, params=premier_params)
    super_response = requests.get(url, headers=headers, params=super_params)

    if super_response.status_code == 200 and champions_response.status_code == 200 and premier_response.status_code == 200:
        premier_fixtures = premier_response.json()["response"]
        champions_fixtures = champions_response.json()["response"]
        super_fixtures = super_response.json()["response"]

        message = "Bugünkü Maçlar:\n\n Süper Lig: \n"
        filtered_super_fixtures = [fixture for fixture in super_fixtures if fixture["fixture"]["status"]["short"] not in ["PST", "CANC", "ABD", "AWD"]]
        if not filtered_super_fixtures:
            message += "Bugün Süper Lig'de maç yok.\n"
        else:
            for fixture in filtered_super_fixtures:
                home_team = fixture["teams"]["home"]["name"]
                away_team = fixture["teams"]["away"]["name"]
                kickoff_time = fixture["fixture"]["date"]
                utc_time = datetime.datetime.fromisoformat(kickoff_time)
                localized_time = utc_time.astimezone(tz)
                kickoff_time = localized_time.strftime("%H:%M")
                message += f"{home_team} vs {away_team} - Başlama saati: {kickoff_time}\n"


        message += "\n\n Şampiyonlar Ligi: \n"
        filtered_champ_fixtures = [fixture for fixture in champions_fixtures if fixture["fixture"]["status"]["short"] not in ["PST", "CANC", "ABD", "AWD"]]
        if not filtered_champ_fixtures:
            message += "Bugün Şampiyonlar Liginde maç yok.\n"
        else:
            for fixture in filtered_champ_fixtures:
                home_team = fixture["teams"]["home"]["name"]
                away_team = fixture["teams"]["away"]["name"]
                kickoff_time = fixture["fixture"]["date"]
                utc_time = datetime.datetime.fromisoformat(kickoff_time)
                localized_time = utc_time.astimezone(tz)
                kickoff_time = localized_time.strftime("%H:%M")
                message += f"{home_team} vs {away_team} - Başlama saati: {kickoff_time}\n"

        message += "\n\n Premier Lig: \n"
        filtered_premier_fixtures = [fixture for fixture in premier_fixtures if fixture["fixture"]["status"]["short"] not in ["PST", "CANC", "ABD", "AWD"]]
        if not filtered_premier_fixtures:
            message += "Bugün Premier Lig'de maç yok.\n"
        else:
            for fixture in filtered_premier_fixtures:
                home_team = fixture["teams"]["home"]["name"]
                away_team = fixture["teams"]["away"]["name"]
                kickoff_time = fixture["fixture"]["date"]
                utc_time = datetime.datetime.fromisoformat(kickoff_time)
                localized_time = utc_time.astimezone(tz)
                kickoff_time = localized_time.strftime("%H:%M")
                message += f"{home_team} vs {away_team} - Başlama saati: {kickoff_time}\n"


        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        
        keyboard = [
            [InlineKeyboardButton("Maçlar", callback_data='matches')],
            [InlineKeyboardButton("Puan Durumu", callback_data='standings')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Merhaba! Ne yapmak istersiniz?', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="API'ye erişilemedi.")

def standings(update, context):
    keyboard = [
        [InlineKeyboardButton("Süper Lig", callback_data='superlig')],
        [InlineKeyboardButton("Premier Lig", callback_data='premierlig')],
        [InlineKeyboardButton("Şampiyonlar Ligi", callback_data='sampiyonlarligi')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text='Hangi ligin puan durumunu görmek istersiniz?', reply_markup=reply_markup)

def handle_button_selection(update, context):
    query = update.callback_query
    league = query.data

    if league == 'superlig':
        league_id = '203'
        league_name = 'Süper Lig'
    elif league == 'premierlig':
        league_id = '39'
        league_name = 'Premier Lig'
    elif league == 'sampiyonlarligi':
        league_id = '2'
        league_name = 'Şampiyonlar Ligi'
    else:
        return

    params = {
        "season": "2022",
        "league": league_id
    }

    response = requests.get(standings_url, headers=headers, params=params)

    if response.status_code == 200:
        standings = response.json()["response"]

        if standings:
            message = f"{standings[0]['league']['country']} {league_name} Puan Durumu:\n\n"

            for team in standings[0]['league']['standings'][0]:
                rank = team['rank']
                team_name = team['team']['name']
                points = team['points']
                message += f"{rank}. {team_name}: {points} puan\n"

            query.message.reply_text(message)
            
            keyboard = [
                [InlineKeyboardButton("Maçlar", callback_data='matches')],
                [InlineKeyboardButton("Puan Durumu", callback_data='standings')],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            query.message.reply_text('Merhaba! Ne yapmak istersiniz?', reply_markup=reply_markup)
        else:
            query.message.reply_text("Puan durumu bulunamadı.")
    else:
        query.message.reply_text("API'ye erişilemedi.")

def main():
    updater = Updater(token="BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    matches_handler = CallbackQueryHandler(matches, pattern='matches')
    standings_handler = CallbackQueryHandler(standings, pattern='standings')
    button_handler = CallbackQueryHandler(handle_button_selection)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(matches_handler)
    dispatcher.add_handler(standings_handler)
    dispatcher.add_handler(button_handler)

    updater.start_polling()

if __name__ == '__main__':
    main()


