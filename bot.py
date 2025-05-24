import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)
from database import Database
from weather_api import get_weather
from config import TELEGRAM_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CITY, PHOTO = range(2)


class WeatherBot:
    def __init__(self):
        self.db = Database()
        self.updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        self.db.add_user(user.id, user.first_name, user.username)

        welcome_message = (
            f"Привет, {user.first_name}!\n"
            "Я бот для поиска погоды. Отправь мне название города, "
            "и я покажу текущую погоду."
        )

        keyboard = [
            [KeyboardButton("Погода в Москве")],
            [KeyboardButton("Погода в Санкт-Петербурге")],
            [KeyboardButton("Мои города")]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(welcome_message, reply_markup=reply_markup)

        return CITY

    def handle_city(self, update: Update, context: CallbackContext) -> int:
        city = update.message.text

        # Удаляем "Погода в " если есть
        if city.startswith("Погода в "):
            city = city[9:]

        try:
            weather_data = get_weather(city)
            self.db.add_search(update.effective_user.id, city)

            response = (
                f"Погода в {city}:\n"
                f"Температура: {weather_data['temp']}°C\n"
                f"Ощущается как: {weather_data['feels_like']}°C\n"
                f"Влажность: {weather_data['humidity']}%\n"
                f"Давление: {weather_data['pressure']} мм рт.ст.\n"
                f"Ветер: {weather_data['wind_speed']} м/с"
            )

            update.message.reply_text(response)

            # Предлагаем отправить фото погоды
            update.message.reply_text(
                "Хотите отправить фото текущей погоды? "
                "Просто отправьте изображение или /cancel чтобы пропустить."
            )

            return PHOTO

        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            update.message.reply_text(
                "Не удалось получить данные о погоде. "
                "Попробуйте другой город."
            )
            return CITY

    def handle_photo(self, update: Update, context: CallbackContext) -> int:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        user_id = update.effective_user.id

        # Сохраняем информацию о фото в БД
        self.db.add_photo(user_id, file_id)

        update.message.reply_text(
            "Спасибо за фото! Вы можете продолжить поиск погоды "
            "в других городах или /cancel чтобы завершить."
        )

        return CITY

    def cancel(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text(
            "Поиск погоды завершен. Нажмите /start чтобы начать заново.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def run(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                CITY: [MessageHandler(Filters.text & ~Filters.command, self.handle_city)],
                PHOTO: [
                    MessageHandler(Filters.photo, self.handle_photo),
                    CommandHandler('cancel', self.cancel)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        self.dispatcher.add_handler(conv_handler)

        # Запуск бота
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    bot = WeatherBot()
    bot.run()