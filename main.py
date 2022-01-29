import telebot
import lowprice
import highprice
import bestdeal

from start import start_func
from dotenv import load_dotenv
import os
from peewee import *

load_dotenv()
bot = telebot.TeleBot(os.getenv('token'))

db = SqliteDatabase('hist.db')  # Создали объект базы данных


# Создали класс, чтобы наследовать от него все таблицы базы данных
class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    # В классе описываем таблицу в базе данных
    name = CharField()
    telegram_id = IntegerField()
    date_info = CharField()
    hotel_results = CharField()


User.create_table()


@bot.message_handler(commands=['start'])
def start_command(message):
    """Функция, выводит приветственное сообщение, при открытии телеграм-бота"""
    start_func(bot, message)


@bot.message_handler(commands=['lowprice'])
def lowprice_command(message):
    """Функция /lowprice, выводит список самых дешевых отелей"""
    lowprice.lowprice_func(bot, message, User)


@bot.message_handler(commands=['highprice'])
def highprice_command(message):
    """Функция /highprice, выводит список самых дорогих отелей"""
    highprice.highprice_func(bot, message, User)


@bot.message_handler(commands=['bestdeal'])
def bestdeal_command(message):
    """Функция /bestdeal, выводит список отелей,
    наиболее подходящих по цене и расположению"""
    bestdeal.bestdeal_func(bot, message, User)


@bot.message_handler(commands=['history'])
def history_command(message):
    """Функция /history, выводит историю запросов пользователя"""
    for user_id in User.select():
        bot.send_message(message.chat.id, user_id.name + '\n' + user_id.date_info + '\n' + user_id.hotel_results)


@bot.message_handler(commands=['help'])
def help_command(message):
    """Функция /help, выводит список доступных команд телеграм-бота"""
    bot.send_message(message.from_user.id, '/help — помощь по командам бота,\n'
                                           '/lowprice — вывод самых дешёвых отелей в городе,\n'
                                           '/highprice — вывод самых дорогих отелей в городе,\n'
                                           '/bestdeal — вывод отелей, наиболее подходящих по цене и '
                                           'расположению от центра.\n'
                                           '/history — вывод истории поиска отелей')


@bot.message_handler(content_types=['text'])
def error_command(message):
    """Функция, выполняется в случае ввода несуществующей команды"""
    bot.send_message(message.chat.id, 'Вы ввели несуществующую '
                                      'команду, чтоб узнать список доступных команд, '
                                      'введите /help')


if __name__ == '__main__':
    """Запуск телеграм-бота"""
    bot.polling(none_stop=True)
