import telebot
from lowprice import lowprice_func
from highprice import highprice_func
from bestdeal import bestdeal_func
import config

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_command(message):
    """Функция, выводит приветственное сообщение, при открытии телеграм-бота"""
    bot.send_message(
        message.chat.id,
        'Привет. Я Телеграм-бот "HotelHelper_bot" и я помогу тебе с выбором отеля.'
        '\n\nЧтоб вывести список доступных команду напиши /help')


@bot.message_handler(commands=['lowprice'])
def lowprice_command(message):
    """Функция /lowprice, выводит список самых дешевых отелей"""
    lowprice_func(bot, message)


@bot.message_handler(commands=['highprice'])
def highprice_command(message):
    """Функция /highprice, выводит список самых дорогих отелей"""
    highprice_func(bot, message)


@bot.message_handler(commands=['bestdeal'])
def bestdeal_command(message):
    """Функция /bestdeal, выводит список отелей,
    наиболее подходящих по цене и расположению"""
    bestdeal_func(bot, message)


@bot.message_handler(commands=['history'])
def history_command(message):
    """Функция /history, выводит историю запросов пользователя"""
    bot.send_message(message.chat.id, 'История поиска')


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
    bot.polling(none_stop=True, interval=0)
