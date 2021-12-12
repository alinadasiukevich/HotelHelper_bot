import telebot


bot = telebot.TeleBot('5018171733:AAGV7p-SOMwCefUN8LzyL_N6KC8wfV3N6lA')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/hello-world":
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /hello-world.")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
