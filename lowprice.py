import requests
import json
from googletrans import Translator
from telebot.types import InputMediaPhoto
translator = Translator()

user_info = {}

# TODO: хорошяа работа с документацией, только давайте опишем параметры, что такое user_message во всех функциях.
# Давайте опишем, например, где-то это максимальное количество, где-то цена и так далее.

def lowprice_func(bot, user_message):
    def main(user_message):
        """Функиция, получает название города"""
        city = bot.send_message(user_message.chat.id, 'Введите город, в котором ищите отель: ')

        bot.register_next_step_handler(city, hotel_count)

    def hotel_count(user_message):
        """Функиция, получает количество отелей"""
        user_info['city'] = (translator.translate(user_message.text, dest='en')).text.lower()
        hotels = bot.send_message(user_message.chat.id,
                                  'Введите количество отелей, которые необходимо вывести в результате (не больше 5): ')
        bot.register_next_step_handler(hotels, photos)

    def photos(user_message):
        """Функция, проверяет правильность введенного количества отелей,
        а также запрашивает информацию о необходимости фотографий"""
        # TODO: вынесем число как константу
        if int(user_message.text) > 5:
            bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
            return hotel_count(user_message)
        user_info['hotel_count'] = user_message.text
        photo = bot.send_message(user_message.chat.id, 'Вам нужны фотографии отеля? (“Да/Нет”): ')
        bot.register_next_step_handler(photo, num_photo)

    def num_photo(user_message):
        """Функция, в случае необходимости, узнает необходимое количество
        фотографий, если фотографии не нужны, выводит результат
        работы телграм-бота без фотографий"""
        if user_message.text.lower() == 'да':
            user_info['need_photo'] = user_message.text
            photo_num = bot.send_message(user_message.chat.id,
                                         'Введите количество фотографий, '
                                         'которые необходимо вывести в результате (не больше 5): ')
            bot.register_next_step_handler(photo_num, result_with_photo)
        else:
            user_info['need_photo'] = user_message.text
            # TODO: все ссылки лучше вынести отдельно, передавая в них требуемые параметры
            url = "https://hotels4.p.rapidapi.com/locations/v2/search"
            querystring = {"query": user_info['city']}
            headers = {
                'x-rapidapi-host': "hotels4.p.rapidapi.com",
                'x-rapidapi-key': "c69c1872abmshf497846dcd25465p192f04jsn091745b8c356"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            data = json.loads(response.text)
            user_destinationId = data['suggestions'][0]['entities'][0]['destinationId']

            url = "https://hotels4.p.rapidapi.com/properties/list"
            querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user_info['hotel_count'],
                           "checkIn": "2022-01-15", "checkOut": "2022-01-16", "adults1": "1", "sortOrder": "PRICE",
                           "currency": "USD"}
            headers = {
                'x-rapidapi-host': "hotels4.p.rapidapi.com",
                'x-rapidapi-key': "c69c1872abmshf497846dcd25465p192f04jsn091745b8c356"
            }
            hotel_response = requests.request("GET", url, headers=headers, params=querystring)
            data = json.loads(hotel_response.text)
            result = data['data']['body']["searchResults"]["results"]
            for i in range(int(user_info['hotel_count'])):
                # TODO: тут лучше вынести строку к отправке в отдельную переменную, чтобы при передаче
                # не городить кучу строк
                bot.send_message(user_message.chat.id, (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                       '\nАдрес: ' + result[i]["address"]["streetAddress"] + ', ' +
                                                        result[i]["address"]["locality"] + ', ' +
                      result[i]["address"]["postalCode"] + ', ' +
                      result[i]["address"]["region"] +
                '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                      ' расстояние: ' + ' ' + result[i]["landmarks"][0]['distance'] +
                '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                      ' расстояние: ' + ' ' + result[i]["landmarks"][1]['distance'] +
                '\nЦена: ' + result[i]["ratePlan"]['price']['current']))

    def result_with_photo(user_message):
        """Функция, проверяет правильность введенного количества фотографий,
        в случае правильного ввода, выводит результат работы телеграм-бота
        с фотографиями"""
        if int(user_message.text) > 5:
            bot.send_message(user_message.chat.id, 'Вы ввели неправильное число.')
            photo_num = bot.send_message(user_message.chat.id,
                                         'Введите количество фотографий, '
                                         'которые необходимо вывести в результате (не больше 5): ')
            bot.register_next_step_handler(photo_num, result_with_photo)
        else:
            user_info['num_photo'] = user_message.text
            url = "https://hotels4.p.rapidapi.com/locations/v2/search"
            querystring = {"query": user_info['city']}
            headers = {
                'x-rapidapi-host': "hotels4.p.rapidapi.com",
                'x-rapidapi-key': "c69c1872abmshf497846dcd25465p192f04jsn091745b8c356"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            data = json.loads(response.text)
            user_destinationId = data['suggestions'][0]['entities'][0]['destinationId']

            url = "https://hotels4.p.rapidapi.com/properties/list"
            querystring = {"destinationId": user_destinationId, "pageNumber": "1", "pageSize": user_info['hotel_count'],
                           "checkIn": "2022-01-15", "checkOut": "2022-01-16", "adults1": "1", "sortOrder": "PRICE",
                           "currency": "USD"}
            headers = {
                'x-rapidapi-host': "hotels4.p.rapidapi.com",
                'x-rapidapi-key': "c69c1872abmshf497846dcd25465p192f04jsn091745b8c356"
            }
            hotel_response = requests.request("GET", url, headers=headers, params=querystring)
            data = json.loads(hotel_response.text)
            result = data['data']['body']["searchResults"]["results"]


            for i in range(int(user_info['hotel_count'])):
                bot.send_message(user_message.chat.id, (str(i + 1) + ' отель: \nНазвание: ' + result[i]["name"] +
                                                        '\nАдрес: ' + result[i]["address"]["streetAddress"] + ', ' +
                                                        result[i]["address"]["locality"] + ', ' +
                                                        result[i]["address"]["postalCode"] + ', ' +
                                                        result[i]["address"]["region"] +
                                                        '\nОт ' + result[i]["landmarks"][0]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][0]['distance'] +
                                                        '\nОт ' + result[i]["landmarks"][1]['label'] + ' ' +
                                                        ' расстояние: ' + ' ' + result[i]["landmarks"][1]['distance'] +
                                                        '\nЦена: ' + result[i]["ratePlan"]['price']['current']))

                url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
                querystring = {"id": data['data']['body']["searchResults"]["results"][i]["id"]}
                headers = {
                    'x-rapidapi-host': "hotels4.p.rapidapi.com",
                    'x-rapidapi-key': "c69c1872abmshf497846dcd25465p192f04jsn091745b8c356"
                }
                response_photo = requests.request("GET", url, headers=headers, params=querystring)
                data_photo = json.loads(response_photo.text)

                media = []
                for j in range(int(user_info['num_photo'])):
                    media.append(InputMediaPhoto((data_photo["hotelImages"][j]['baseUrl']).format(size= 'z')))
                bot.send_media_group(user_message.chat.id, media)


    main(user_message)
