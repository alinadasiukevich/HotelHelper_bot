import json
from googletrans import Translator
from telebot.types import InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, datetime
import api
from users import Users
import re

LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
translator = Translator()


def highprice_func(bot, user_message, User):
    """Функция, получает название города

    user_message (str): команда /highprice"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.user_id = user_id
    user.command = 'Highprice'
    user.time_of_use = datetime.today()
    bot.send_message(user_message.from_user.id, 'Введите город, в котором ищите отель: ')

    bot.register_next_step_handler(user_message, check_in_dates, bot, User)


def check_in_dates(user_message, bot, User):
    """Функция, получает желаемую дату заезда

    user_message (str): название города"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.city = (translator.translate(user_message.text.lower(), dest='en')).text

    def start(m):
        calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').build()
        bot.send_message(m.chat.id,
                             f"Выберите {LSTEP[step]} заезда",
                             reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
    def cal(c):
        result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').process(c.data)
        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]} заезда",
                                      c.message.chat.id,
                                      c.message.message_id,
                                      reply_markup=key)
        elif result:
            user.check_in = result
            bot.edit_message_text(f"Дата заезда {result}",
                                                 c.message.chat.id,
                                                 c.message.message_id)
            check_out_dates(user_message, bot, User)

    start(user_message)


def check_out_dates(user_message, bot, User):
    """Функция, получает желаемую дату выезда

    user_message (str): дата заезда"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)

    def start1(m):
        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=user.check_in, locale='ru').build()
        bot.send_message(m.chat.id,
                             f"Выберите {LSTEP[step]} выезда",
                             reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
    def cal1(c):
        result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=user.check_in, locale='ru').process(c.data)
        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]} выезда",
                                      c.message.chat.id,
                                      c.message.message_id,
                                      reply_markup=key)
        elif result:
            user.check_out = result
            bot.edit_message_text(f"Дата выезда {result}",
                                                  c.message.chat.id,
                                                  c.message.message_id)
            hotel_count(user_message, bot, User)
    start1(user_message)


def hotel_count(user_message, bot, User):
    """Функция, получает количество отелей

    user_message (str): дата выезда"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    bot.send_message(user_message.from_user.id,
                              'Введите количество отелей, которые необходимо вывести в результате (не больше 5): ')
    bot.register_next_step_handler(user_message, photos, bot, User)


def photos(user_message, bot, User):
    """Функция, проверяет правильность введенного количества отелей,
    а также запрашивает информацию о необходимости фотографий

    user_message (int): количество отелей"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    HOTELS_NUM = int(user_message.text)
    if HOTELS_NUM > 5:
        bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
        return hotel_count(user_message, bot, User)
    user.hotel_count = user_message.text
    photo = bot.send_message(user_message.from_user.id, 'Вам нужны фотографии отеля? (“Да/Нет”): ')
    bot.register_next_step_handler(photo, num_photo, bot, User)


def num_photo(user_message, bot, User):
    """Функция, в случае необходимости, узнает необходимое количество
    фотографий, если фотографии не нужны, выводит результат
    работы телграм-бота без фотографий

    user_message (str): необходимость фотографий (да/нет)"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    if user_message.text.lower() == 'да':
        user.need_photo = user_message.text
        photo_num = bot.send_message(user_message.from_user.id,
                                     'Введите количество фотографий, '
                                     'которые необходимо вывести в результате (не больше 5): ')
        bot.register_next_step_handler(photo_num, result_with_photo, bot, User)
    else:
        bot.send_message(user_message.chat.id, 'Ищем отели по вашим критериям.'
                                               '\nЭто может занять немного времени.')
        user.need_photo = user_message.text
        querystring = {"query": user.city}
        response = api.get_location(querystring)
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, response.text)
        if find:
            data = json.loads(f"{{{find[0]}}}")
        user_destinationId = data['entities'][0]['destinationId']
        querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user.hotel_count,
                       "checkIn": "2022-01-15", "checkOut": "2022-01-16", "adults1": "1",
                       "sortOrder": "PRICE_HIGHEST_FIRST", "currency": "USD"}

        hotel_response = api.get_properties(querystring)
        pattern = r'(?<=,)"results":.+?(?=,"pagination")'
        find_hotel = re.search(pattern, hotel_response.text)
        if find_hotel:
            data_hotel = json.loads(f"{{{find_hotel[0]}}}")

        result = data_hotel["results"]
        for i in range(int(user.hotel_count)):
            if 'streetAddress' in result[i]['address']:
                expensive_hotels = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                   '\nАдрес: ' + result[i]['address']['streetAddress'] + ', ' +
                                                    result[i]['address']['locality'] + ', ' +
                                                    result[i]['address']['postalCode'] + ', ' +
                                                    result[i]['address']['region'] +
                                                    '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                    ' расстояние: ' + ' ' + result[i]["landmarks"][0]['distance'] +
                                                    '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                    ' расстояние: ' + ' ' + result[i]["landmarks"][1]['distance'] +
                                                    '\nЦена за сутки: ' + result[i]['ratePlan']['price']['current'])
                user.hotels_res.append(result[i]["name"])
                bot.send_message(user_message.chat.id, expensive_hotels)
            else:
                expensive_hotels = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                        '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][0][
                                                            'distance'] +
                                                        '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][1][
                                                            'distance'] +
                                                        '\nЦена за сутки: ' + result[i]['ratePlan']['price']['current'])
                user.hotels_res.append(result[i]["name"])
                bot.send_message(user_message.chat.id, expensive_hotels)
            User.create(name=user.command, telegram_id=user.user_id,
                            date_info=user.time_of_use, hotel_results=str(user.hotels_res))


def result_with_photo(user_message, bot, User):
    """Функция, проверяет правильность введенного количества фотографий,
    в случае правильного ввода, выводит результат работы телеграм-бота
    с фотографиями

    user_message (int): количество фотографий"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    PHOTO_NUM = int(user_message.text)
    if PHOTO_NUM > 5:
        bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
        bot.send_message(user_message.from_user.id,
                                     'Введите количество фотографий, '
                                     'которые необходимо вывести в результате (не больше 5): ')
        bot.register_next_step_handler(user_message, result_with_photo, User)
    else:
        bot.send_message(user_message.chat.id, 'Ищем отели по вашим критериям.'
                                               '\nЭто может занять немного времени.')
        user.num_photo = user_message.text
        querystring = {"query": user.city}
        response = api.get_location(querystring)
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, response.text)
        if find:
            data = json.loads(f"{{{find[0]}}}")
        user_destinationId = data['entities'][0]['destinationId']
        querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user.hotel_count,
                       "checkIn": "2022-01-15", "checkOut": "2022-01-16", "adults1": "1",
                       "sortOrder": "PRICE_HIGHEST_FIRST", "currency": "USD"}

        hotel_response = api.get_properties(querystring)
        pattern = r'(?<=,)"results":.+?(?=,"pagination")'
        find_hotel = re.search(pattern, hotel_response.text)
        if find_hotel:
            data_hotel = json.loads(f"{{{find_hotel[0]}}}")
        result = data_hotel["results"]

        for i in range(int(user.hotel_count)):

            if 'streetAddress' in result[i]['address']:
                expensive_hotels_photo = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                        '\nАдрес: ' + result[i]['address']['streetAddress'] + ', ' +
                                                        result[i]['address']['locality'] + ', ' +
                                                        result[i]['address']['postalCode'] + ', ' +
                                                        result[i]['address']['region'] +
                                                        '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][0][
                                                            'distance'] +
                                                        '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][1][
                                                            'distance'] +
                                                        '\nЦена за сутки: ' + result[i]['ratePlan']['price']['current'])
                user.hotels_res.append(result[i]["name"])
                bot.send_message(user_message.chat.id, expensive_hotels_photo)
            else:
                expensive_hotels_photo = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                        '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][0][
                                                            'distance'] +
                                                        '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][1][
                                                            'distance'] +
                                                        '\nЦена за сутки: ' + result[i]['ratePlan']['price']['current'])
                user.hotels_res.append(result[i]["name"])
                bot.send_message(user_message.chat.id, expensive_hotels_photo)

            querystring = {"id": data_hotel["results"][i]["id"]}
            response_photo = api.get_photos(querystring)
            pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages")'
            find = re.search(pattern, response_photo.text)
            if find:
                data_photo = json.loads(f"{{{find[0]}}}")
            media = []
            for j in range(int(user.num_photo)):
                media.append(InputMediaPhoto((data_photo["hotelImages"][j]['baseUrl']).format(size='z')))
            bot.send_media_group(user_message.chat.id, media)
        User.create(name=user.command, telegram_id=user.user_id,
                    date_info=user.time_of_use, hotel_results=str(user.hotels_res))
