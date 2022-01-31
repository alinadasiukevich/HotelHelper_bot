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


def bestdeal_func(bot, user_message, User, db):
    """Функция, получает название города

    user_message (str): команда /bestdeal"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.user_id = user_id
    user.command = 'Bestdeal'
    user.time_of_use = datetime.today()
    bot.send_message(user_message.from_user.id, 'Введите город, в котором ищите отель: ')

    bot.register_next_step_handler(user_message, check_in_dates, bot, User, db)


def check_in_dates(user_message, bot, User, db):
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
            check_out_dates(user_message, bot, User, db)
    start(user_message)


def check_out_dates(user_message, bot, User, db):
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
            min_price(user_message, bot, User, db)
    start1(user_message)


def min_price(user_message, bot, User, db):
    """Функция, получает минимальную цену в долларах

    user_message(str): дата выезда"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    bot.send_message(user_message.from_user.id,
                              'Введите минимальную цену отеля за сутки, подходящую для вас (в $) ')
    bot.register_next_step_handler(user_message, max_price, bot, User, db)


def max_price(user_message, bot, User, db):
    """Функция, получает максимальную цену в долларах

    user_message(int): Минимальная цена """
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.price_min = user_message.text
    bot.send_message(user_message.from_user.id,
                                         'Введите максимальную цену отеля за сутки, подходящую для вас (в $) ')
    bot.register_next_step_handler(user_message, min_distance, bot, User, db)


def min_distance(user_message, bot, User, db):
    """Функция, получает минимальное расстояние в км.

    user_message(int): Максимальная цена """
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.price_max = user_message.text
    if int(user.price_min) > int(user.price_max):
        bot.send_message(user_message.chat.id, 'Максимальная цена не может быть меньше минимальной.'
                                               'Попробуйте еще раз.')
        return min_price(user_message, bot, User, db)
    bot.send_message(user_message.from_user.id,
                                'Введите минимальное расстояние отеля от центра, подходящее для вас (в км.) ')
    bot.register_next_step_handler(user_message, max_distance, bot, User, db)


def max_distance(user_message, bot, User, db):
    """Функция, получает максимальное расстояние в км.

    user_message(float): минимальное расстояние """
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.distance_min = user_message.text
    bot.send_message(user_message.from_user.id,
                                'Введите максимальное расстояние отеля от центра, подходящее для вас (в км.) ')
    bot.register_next_step_handler(user_message, hotel_count, bot, User, db)


def hotel_count(user_message, bot, User, db):
    """Функция, получает количество отелей

    user_message(float): максимальное расстояние"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    user.distance_max = user_message.text
    if float(user.distance_min) > float(user.distance_max):
        bot.send_message(user_message.chat.id, 'Максимальное расстояние не может быть меньше минимального.'
                                               'Попробуйте еще раз.')
        return min_distance(user_message, bot, User, db)
    bot.send_message(user_message.from_user.id,
                              'Введите количество отелей, которые необходимо вывести в результате (не больше 5): ')
    bot.register_next_step_handler(user_message, photos, bot, User, db)


def photos(user_message, bot, User, db):
    """Функция, проверяет правильность введенного количества отелей,
    а также запрашивает информацию о необходимости фотографий

    user_message (int): количество отелей"""
    user_id = user_message.chat.id
    user = Users.get_user(user_id)
    HOTELS_NUM = int(user_message.text)
    if HOTELS_NUM > 5:
        bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
        return hotel_count(user_message, bot, User, db)
    user.hotel_count = user_message.text
    bot.send_message(user_message.chat.id, 'Вам нужны фотографии отеля? (“Да/Нет”): ')
    bot.register_next_step_handler(user_message, num_photo, bot, User, db)


def num_photo(user_message, bot, User, db):
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
        bot.register_next_step_handler(photo_num, result_with_photo, bot, User, db)
    else:
        bot.send_message(user_message.chat.id, 'Ищем отели по вашим критериям.'
                                               '\nЭто может занять немного времени.')
        user.need_photo = user_message.text

        querystring = {"query": user.city}

        response = api.request_to_api(api.url_locations, api.headers, querystring)
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, response.text)
        if find:
            data = json.loads(f"{{{find[0]}}}")
        user_destinationId = data['entities'][0]['destinationId']
        querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user.hotel_count,
                       "checkIn": user.check_in, "checkOut": user.check_out, "adults1": "1",
                       "priceMin": user.price_min, "priceMax": user.price_max,
                       "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "USD"}

        hotel_response = api.request_to_api(api.url_properties, api.headers, querystring)
        pattern = r'(?<=,)"results":.+?(?=,"pagination")'
        find_hotel = re.search(pattern, hotel_response.text)
        if find_hotel:
            data_hotel = json.loads(f"{{{find_hotel[0]}}}")
        result = data_hotel["results"]
        for i in range(int(user.hotel_count)):
            dist = result[i]["landmarks"][0]['distance']
            dist_from_cent = float(dist.replace(' км', '').replace(',', '.'))

            if float(user.distance_min) < dist_from_cent < float(user.distance_max) and 'ratePlan' in result[i] and 'streetAddress' in result[i]["address"]:
                deal_hotels = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                 '\nАдрес: ' + result[i]["address"]["streetAddress"] + ', ' +
                 result[i]["address"]["locality"] + ', ' +
                 result[i]["address"]["postalCode"] + ', ' +
                 result[i]["address"]["region"] +
                 '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                 ' расстояние: ' + ' ' + result[i]["landmarks"][0]['distance'] +
                 '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                 ' расстояние: ' + ' ' + result[i]["landmarks"][1]['distance'] +
                 '\nЦена за сутки: ' + result[i]["ratePlan"]['price']['current'])
                user.hotels_res.append(result[i]["name"])
                bot.send_message(user_message.chat.id, deal_hotels)
        with db:
            User.create(name=user.command, telegram_id=user.user_id, date_info=user.time_of_use, hotel_results=str(user.hotels_res))


def result_with_photo(user_message, bot, User, db):
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
        bot.register_next_step_handler(user_message, result_with_photo, bot, User, db)
    else:
        bot.send_message(user_message.chat.id, 'Ищем отели по вашим критериям.'
                                               '\nЭто может занять немного времени.')
        user.num_photo = user_message.text

        querystring = {"query": user.city}

        response = api.request_to_api(api.url_locations, api.headers, querystring)
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, response.text)
        if find:
            data = json.loads(f"{{{find[0]}}}")
        user_destinationId = data['entities'][0]['destinationId']
        querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user.hotel_count,
                       "checkIn": user.check_in, "checkOut": user.check_out, "adults1": "1",
                       "priceMin": user.price_min, "priceMax": user.price_max,
                       "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "USD"}

        hotel_response = api.request_to_api(api.url_properties, api.headers, querystring)
        pattern = r'(?<=,)"results":.+?(?=,"pagination")'
        find_hotel = re.search(pattern, hotel_response.text)
        if find_hotel:
            data_hotel = json.loads(f"{{{find_hotel[0]}}}")
        result = data_hotel["results"]
        for i in range(int(user.hotel_count)):
            dist = result[i]["landmarks"][0]['distance']
            dist_from_cent = float(dist.replace(' км', '').replace(',', '.'))

            if float(user.distance_min) < dist_from_cent < float(user.distance_max) and 'ratePlan' in \
                    result[i]:
                cheap_hotels_photo = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                        '\nАдрес: ' + result[i]["address"]["streetAddress"] + ', ' +
                                                        result[i]["address"]["locality"] + ', ' +
                                                        result[i]["address"]["postalCode"] + ', ' +
                                                        result[i]["address"]["region"] +
                                                        '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][0]['distance'] +
                                                        '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][1]['distance'] +
                                                        '\nЦена за сутки: ' + result[i]["ratePlan"]['price']['current'])
                user.hotels_res.append(result[i]["name"])
                bot.send_message(user_message.chat.id, cheap_hotels_photo)
            querystring = {"id": data['data']['body']["searchResults"]["results"][i]["id"]}
            response_photo = api.request_to_api(api.url_get_photos, api.headers, querystring)
            pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages")'
            find = re.search(pattern, response_photo.text)
            if find:
                data_photo = json.loads(f"{{{find[0]}}}")
            media = []
            for j in range(int(user.num_photo)):
                media.append(InputMediaPhoto((data_photo["hotelImages"][j]['baseUrl']).format(size='z')))
            bot.send_media_group(user_message.chat.id, media)
        with db:
            User.create(name=user.command, telegram_id=user.user_id,
                    date_info=user.time_of_use, hotel_results=str(user.hotels_res))
