import telebot
from lowprice import lowprice_func

bot = telebot.TeleBot('5018171733:AAGV7p-SOMwCefUN8LzyL_N6KC8wfV3N6lA')


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        'Привет. Я Телеграм-бот "HotelHelper_bot" и я помогу тебе с выбором отеля.'
        '\n\nЧтоб вывести список доступных команду напиши /help')


@bot.message_handler(commands=['lowprice'])
def lowprice_command(message):
    lowprice_func(bot, message)


@bot.message_handler(commands=['highprice'])
def highprice_command(message):
    bot.send_message(message.chat.id, 'Самые дорогие отели')


@bot.message_handler(commands=['bestdeal'])
def bestdeal_command(message):
    bot.send_message(message.chat.id, 'Самые подходящие отели')


@bot.message_handler(commands=['history'])
def history_command(message):
    bot.send_message(message.chat.id, 'История поиска')


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, '/help — помощь по командам бота,\n'
                                            '/lowprice — вывод самых дешёвых отелей в городе,\n'
                                            '/highprice — вывод самых дорогих отелей в городе,\n'
                                            '/bestdeal — вывод отелей, наиболее подходящих по цене и '
                                            'расположению от центра.\n'
                                            '/history — вывод истории поиска отелей')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
