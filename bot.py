import logging
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import schedule
import time
from PIL import Image
from io import BytesIO

# Configurar el bot y logging
TOKEN = '8147070708:AAFySXxU93V29wu-F3iA4wiuq0vZ5pcXjBY'
NEWS_API_KEY = '073ca4c0763942e0b4ecc850f854b349'  # Usa una API como NewsAPI
CHAT_ID = '7282392680'  # El chat ID donde se enviarán las noticias

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para obtener noticias de fútbol
def get_football_news():
    url = f"https://newsapi.org/v2/everything?q=football&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    news_data = response.json()

    if news_data['status'] == 'ok':
        articles = news_data['articles'][:5]  # Limitar a las 5 primeras noticias
        return articles
    else:
        return []

# Función para enviar noticias al chat de Telegram
def send_news(bot):
    news_list = get_football_news()
    if news_list:
        for news in news_list:
            title = news['title']
            description = news['description']
            url = news['url']
            image_url = news.get('urlToImage')

            # Descargar la imagen
            if image_url:
                try:
                    image_response = requests.get(image_url)
                    img = Image.open(BytesIO(image_response.content))
                    img.save('temp_image.jpg')
                    bot.send_photo(chat_id=CHAT_ID, photo=open('temp_image.jpg', 'rb'), caption=f"{title}\n\n{description}\n{url}")
                except Exception as e:
                    logger.error(f"Error al descargar la imagen: {e}")
            else:
                bot.send_message(chat_id=CHAT_ID, text=f"{title}\n\n{description}\n{url}")
    else:
        bot.send_message(chat_id=CHAT_ID, text="No hay noticias de fútbol disponibles en este momento.")

# Comando /start para iniciar el bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('¡Bot de noticias de fútbol activado! Te enviaré noticias cada hora.')

# Programar la tarea para obtener noticias cada hora
def schedule_news(bot):
    schedule.every(1).hours.do(lambda: send_news(bot))

    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    bot = Bot(token=TOKEN)

    # Inicializar el Updater
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Registrar comandos
    dispatcher.add_handler(CommandHandler("start", start))

    # Iniciar el bot
    updater.start_polling()

    # Ejecutar la programación de noticias cada hora
    schedule_news(bot)

    # Mantener el bot ejecutándose
    updater.idle()

if __name__ == '__main__':
    main()
