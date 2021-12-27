import requests
import json
from googletrans import Translator
from telebot.types import InputMediaPhoto
import config


translator = Translator()
user_info = {}
url_locations = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/list"
url_get_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

def highprice_func(bot, user_message):
    """Функция, выводит самые дорогие отели, согласно заданным параметрам пользователя"""

    def main(user_message):
        """Функция, получает название города

        user_message (str): команда /highprice"""
        city = bot.send_message(user_message.chat.id, 'Введите город, в котором ищите отель: ')

        bot.register_next_step_handler(city, hotel_count)

    def hotel_count(user_message):
        """Функция, получает количество отелей

        user_message (str): Название города"""
        user_info['city'] = (translator.translate(user_message.text.lower(), dest='en')).text
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
            user_info['need_photo'] = user_message.text
            querystring = {"query": user_info['city']}
            response = requests.request("GET", url_locations, headers=config.headers, params=querystring)
            data = json.loads(response.text)
            user_destinationId = data['suggestions'][0]['entities'][0]['destinationId']


            querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user_info['hotel_count'],
                           "checkIn": "2022-01-15", "checkOut": "2022-01-16", "adults1": "1",
                           "sortOrder": "PRICE_HIGHEST_FIRST", "currency": "USD"}

            hotel_response = requests.request("GET", url_properties, headers=config.headers, params=querystring)
            data = json.loads(hotel_response.text)
            result = data['data']['body']["searchResults"]["results"]
            for i in range(int(user_info['hotel_count'])):

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
                                                        '\nЦена: ' + result[i]['ratePlan']['price']['current'])
                    bot.send_message(user_message.chat.id, expensive_hotels)
                else:
                    expensive_hotels = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                            '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                            ' расстояние: ' + ' ' + result[i]["landmarks"][0][
                                                                'distance'] +
                                                            '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                            ' расстояние: ' + ' ' + result[i]["landmarks"][1][
                                                                'distance'] +
                                                            '\nЦена: ' + result[i]['ratePlan']['price']['current'])
                    bot.send_message(user_message.chat.id, expensive_hotels)

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
            user_info['num_photo'] = user_message.text

            querystring = {"query": user_info['city']}

            response = requests.request("GET", url_locations, headers=config.headers, params=querystring)
            data = json.loads(response.text)
            user_destinationId = data['suggestions'][0]['entities'][0]['destinationId']


            querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user_info['hotel_count'],
                           "checkIn": "2022-01-15", "checkOut": "2022-01-16", "adults1": "1",
                           "sortOrder": "PRICE_HIGHEST_FIRST", "currency": "USD"}

            hotel_response = requests.request("GET", url_properties, headers=config.headers, params=querystring)
            data = json.loads(hotel_response.text)
            result = data['data']['body']["searchResults"]["results"]

            for i in range(int(user_info['hotel_count'])):

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
                                                            '\nЦена: ' + result[i]['ratePlan']['price']['current'])
                    bot.send_message(user_message.chat.id, expensive_hotels_photo)
                else:
                    expensive_hotels_photo = (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                            '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                            ' расстояние: ' + ' ' + result[i]["landmarks"][0][
                                                                'distance'] +
                                                            '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                            ' расстояние: ' + ' ' + result[i]["landmarks"][1][
                                                                'distance'] +
                                                            '\nЦена: ' + result[i]['ratePlan']['price']['current'])
                    bot.send_message(user_message.chat.id, expensive_hotels_photo)


                querystring = {"id": data['data']['body']["searchResults"]["results"][i]["id"]}

                response_photo = requests.request("GET", url_get_photos, headers=config.headers, params=querystring)
                data_photo = json.loads(response_photo.text)

                media = []
                for j in range(int(user_info['num_photo'])):
                    media.append(InputMediaPhoto((data_photo["hotelImages"][j]['baseUrl']).format(size='z')))
                bot.send_media_group(user_message.chat.id, media)

    main(user_message)
