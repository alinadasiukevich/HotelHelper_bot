import requests
import json
from googletrans import Translator
from telebot.types import InputMediaPhoto
import config
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, datetime


LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
translator = Translator()
user_info = {}
url_locations = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/list"
url_get_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

def bestdeal_func(bot, user_message, sql):
    """Функция, выводит отели, наиболее подходящих по цене и расположению от
    центра"""
    command_name = 'Bestdeal'
    date_info = datetime.today()
    hotels_name = []
    def main(user_message):
        """Функция, получает название города

        user_message (str): команда /bestdeal"""
        city = bot.send_message(user_message.chat.id, 'Введите город, в котором ищите отель: ')

        bot.register_next_step_handler(city, check_in_dates)


    def check_in_dates(user_message):
        """Функция, получает желаемую дату заезда

        user_message (str): название города"""
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

                user_info['check_in'] = result
                check_in = bot.edit_message_text(f"Дата заезда {result}",
                                                 c.message.chat.id,
                                                 c.message.message_id)
                check_out_dates(user_message)

        start(user_message)

    def check_out_dates(user_message):
        """Функция, получает желаемую дату выезда

        user_message (str): дата заезда"""
        def start1(m):
            calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=user_info['check_in'], locale='ru').build()
            bot.send_message(m.chat.id,
                             f"Выберите {LSTEP[step]} выезда",
                             reply_markup=calendar)

        @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
        def cal1(c):
            result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=user_info['check_in'], locale='ru').process(c.data)
            if not result and key:
                bot.edit_message_text(f"Выберите {LSTEP[step]} выезда",
                                      c.message.chat.id,
                                      c.message.message_id,
                                      reply_markup=key)
            elif result:
                user_info['check_out'] = result
                check_out = bot.edit_message_text(f"Дата выезда {result}",
                                                  c.message.chat.id,
                                                  c.message.message_id)
                min_price(user_message)

        start1(user_message)

    def min_price(user_message):
        """Функция, получает минимальную цену в долларах

        user_message(str): дата выезда"""
        user_info['city'] = (translator.translate((user_message.text).lower(), dest='en')).text
        minprice = bot.send_message(user_message.chat.id,
                                  'Введите минимальную цену отеля за сутки, подходящую для вас (в $) ')
        bot.register_next_step_handler(minprice, max_price)

    def max_price(user_message):
        """Функция, получает максимальную цену в долларах

        user_message(int): Минимальная цена """
        user_info['minprice'] = user_message.text
        maxprice = bot.send_message(user_message.chat.id,
                                             'Введите максимальную цену отеля за сутки, подходящую для вас (в $) ')
        bot.register_next_step_handler(maxprice, min_distance)

    def min_distance(user_message):
        """Функция, получает минимальное расстояние в км.

        user_message(int): Максимальная цена """
        user_info['maxprice'] = user_message.text
        if int(user_info["minprice"]) > int(user_info['maxprice']):
            bot.send_message(user_message.chat.id, 'Максимальная цена не может быть меньше минимальной.'
                                                   'Попробуйте еще раз.')
            return min_price(user_message)
        mindistance = bot.send_message(user_message.chat.id,
                                    'Введите минимальное расстояние отеля от центра, подходящее для вас (в км.) ')
        bot.register_next_step_handler(mindistance, max_distance)

    def max_distance(user_message):
        """Функция, получает максимальное расстояние в км.

        user_message(float): минимальное расстояние """
        user_info['mindistance'] = user_message.text
        maxdistance = bot.send_message(user_message.chat.id,
                                    'Введите максимальное расстояние отеля от центра, подходящее для вас (в км.) ')
        bot.register_next_step_handler(maxdistance, hotel_count)

    def hotel_count(user_message):
        """Функция, получает количество отелей

        user_message(float): максимальное расстояние"""
        user_info['maxdistance'] = user_message.text
        if float(user_info['mindistance']) > float(user_info['maxdistance']):
            bot.send_message(user_message.chat.id, 'Максимальное расстояние не может быть меньше минимального.'
                                                   'Попробуйте еще раз.')
            return min_distance(user_message)

        hotels = bot.send_message(user_message.chat.id,
                                  'Введите количество отелей, которые необходимо вывести в результате (не больше 5): ')
        bot.register_next_step_handler(hotels, photos)

    def photos(user_message):
        """Функция, проверяет правильность введенного количества отелей,
        а также запрашивает информацию о необходимости фотографий

        user_message (int): количество отелей"""
        HOTELS_NUM = int(user_message.text)
        if HOTELS_NUM > 5:
            bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
            return hotel_count(user_message)
        user_info['hotel_count'] = user_message.text
        photo = bot.send_message(user_message.chat.id, 'Вам нужны фотографии отеля? (“Да/Нет”): ')
        bot.register_next_step_handler(photo, num_photo)

    def num_photo(user_message):
        """Функция, в случае необходимости, узнает необходимое количество
        фотографий, если фотографии не нужны, выводит результат
        работы телграм-бота без фотографий

        user_message (str): необходимость фотографий (да/нет)"""
        if user_message.text.lower() == 'да':
            user_info['need_photo'] = user_message.text
            photo_num = bot.send_message(user_message.chat.id,
                                         'Введите количество фотографий, '
                                         'которые необходимо вывести в результате (не больше 5): ')
            bot.register_next_step_handler(photo_num, result_with_photo)
        else:
            bot.send_message(user_message.chat.id, 'Ищем отели по вашим критериям.'
                                                   '\nЭто может занять немного времени.')
            user_info['need_photo'] = user_message.text

            querystring = {"query": user_info['city']}

            response = requests.request("GET", url_locations, headers=config.headers, params=querystring)
            data = json.loads(response.text)
            user_destinationID = data['suggestions'][0]['entities'][0]['destinationId']

            querystring = {"destinationId": user_destinationID, "pageNumber": "1", "pageSize": user_info['hotel_count'],
                           "checkIn": user_info['check_in'], "checkOut": user_info['check_out'], "adults1": "1",
                           "priceMin": user_info['minprice'], "priceMax": user_info['maxprice'],
                           "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "USD"}


            hotel_response = requests.request("GET", url_properties, headers=config.headers, params=querystring)


            data = json.loads(hotel_response.text)
            result = data['data']['body']["searchResults"]["results"]
            for i in range(int(user_info['hotel_count'])):
                dist = result[i]["landmarks"][0]['distance']
                dist_from_cent = float(dist.replace(' км', '').replace(',', '.'))

                if float(user_info['mindistance']) < dist_from_cent < float(user_info['maxdistance']) and 'ratePlan' in result[i]:
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
                    hotels_name.append(result[i]["name"])
                    bot.send_message(user_message.chat.id, deal_hotels)

            info = (command_name, str(date_info), str(hotels_name))
            sql.execute(f"INSERT INTO commands VALUES (?, ?, ?)", info)
    def result_with_photo(user_message):
        """Функция, проверяет правильность введенного количества фотографий,
        в случае правильного ввода, выводит результат работы телеграм-бота
        с фотографиями

        user_message (int): количество фотографий"""
        PHOTO_NUM = int(user_message.text)
        if PHOTO_NUM > 5:
            bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
            photo_num = bot.send_message(user_message.chat.id,
                                         'Введите количество фотографий, '
                                         'которые необходимо вывести в результате (не больше 5): ')
            bot.register_next_step_handler(photo_num, result_with_photo)
        else:
            bot.send_message(user_message.chat.id, 'Ищем отели по вашим критериям.'
                                                   '\nЭто может занять немного времени.')
            user_info['num_photo'] = user_message.text

            querystring = {"query": user_info['city']}

            response = requests.request("GET", url_locations, headers=config.headers, params=querystring)
            data = json.loads(response.text)
            user_destinationID = data['suggestions'][0]['entities'][0]['destinationId']

            querystring = {"destinationId": user_destinationID, "pageNumber": "1", "pageSize": user_info['hotel_count'],
                           "checkIn": user_info['check_in'], "checkOut": user_info['check_out'], "adults1": "1",
                           "priceMin": user_info['minprice'], "priceMax": user_info['maxprice'],
                           "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "USD"}

            hotel_response = requests.request("GET", url_properties, headers=config.headers, params=querystring)

            data = json.loads(hotel_response.text)
            result = data['data']['body']["searchResults"]["results"]
            for i in range(int(user_info['hotel_count'])):
                dist = result[i]["landmarks"][0]['distance']
                dist_from_cent = float(dist.replace(' км', '').replace(',', '.'))

                if float(user_info['mindistance']) < dist_from_cent < float(user_info['maxdistance']) and 'ratePlan' in \
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
                    hotels_name.append(result[i]["name"])
                    bot.send_message(user_message.chat.id, cheap_hotels_photo)
                info = (command_name, str(date_info), str(hotels_name))
                sql.execute(f"INSERT INTO commands VALUES (?, ?, ?)", info)

                querystring = {"id": data['data']['body']["searchResults"]["results"][i]["id"]}

                response_photo = requests.request("GET", url_get_photos, headers=config.headers, params=querystring)
                data_photo = json.loads(response_photo.text)

                media = []
                for j in range(int(user_info['num_photo'])):
                    media.append(InputMediaPhoto((data_photo["hotelImages"][j]['baseUrl']).format(size= 'z')))
                bot.send_media_group(user_message.chat.id, media)


    main(user_message)