def start_func(bot, user_message):
    """Функция, выводится при запуске телеграм-бота"""
    bot.send_message(
        user_message.chat.id,
        'Привет. Я Телеграм-бот "HotelHelper_bot" и я помогу тебе с выбором отеля.'
        '\n\nЧтоб вывести список доступных команду напиши /help')