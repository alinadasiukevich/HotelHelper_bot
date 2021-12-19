def lowprice_func(bot, user_message):
    def main(user_message):
        city = bot.send_message(user_message.chat.id, 'Введите город, в котором ищите отель: ')

        bot.register_next_step_handler(city, hotel_count)

    def hotel_count(user_message):
        hotels = bot.send_message(user_message.chat.id,
                                  'Введите количество отелей, которые необходимо вывести в результате (не больше 5): ')
        bot.register_next_step_handler(hotels, photos)

    def photos(user_message):
        if int(user_message.text) > 5:
            msg = bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
            return hotel_count(user_message)
        photo = bot.send_message(user_message.chat.id, 'Вам нужны фотографии отеля? (“Да/Нет”): ')
        bot.register_next_step_handler(photo, num_photo)

    def num_photo(user_message):
        if user_message.text == 'да':
            photo_num = bot.send_message(user_message.chat.id,
                                         'Введите количество фотографий, '
                                         'которые необходимо вывести в результате (не больше 5): ')
            bot.register_next_step_handler(photo_num, result_with_photo)
        else:
            bot.send_message(user_message.chat.id, 'Выводит самые дешевые отели без фоток')

    def result_with_photo(user_message):
        if int(user_message.text) > 5:
            msg = bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
            photo_num = bot.send_message(user_message.chat.id,
                                         'Введите количество фотографий, '
                                         'которые необходимо вывести в результате (не больше 5): ')
            bot.register_next_step_handler(photo_num, result_with_photo)
        else:
            bot.send_message(user_message.chat.id, 'Выводит самые дешевые отели с фотками')

    main(user_message)

