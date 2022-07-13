import telebot
from telebot import types

from random import seed, randint

import requests
import json


class FilmsBot:
    def __init__(self):
        self.bot = telebot.TeleBot('5049347663:AAHrg7oBpxXO_w5oeWaptAINCbkCKNojdYo')
        self.owner_id = 1140886668

        self.genres = [28, 37, 10752, 9648, 99, 18, 36, 35, 80, 10749, 10402, 16, 12, 10751, 10770, 53, 27, 878, 14]

        self.title = None
        self.description = None
        self.image = None

        self.api_key = '51201bea16768dcaccd8a5c90e6c7972'
        self.language = 'ru-RU'

        self.genres_values = {28: "Боевик",
                              37: "Вестерн",
                              10752: "Военный",
                              9648: "Детектив",
                              99: "Документальный",
                              18: "Драма",
                              36: "История",
                              35: "Комедия",
                              80: "Криминал",
                              10749: "Мелодрама",
                              10402: "Музыка",
                              16: "Мультфильм",
                              12: "Приключения",
                              10751: "Семейный",
                              10770: "Телефильм",
                              53: "Триллер",
                              27: "Ужасы",
                              878: "Фантастика",
                              14: "Фэнтези"}

        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.InlineKeyboardButton("Сменить жанр")
            markup.add(button1)
            mess1 = 'Приветсвую! Давай вкратце расскажу, что я умею.\nТы выбираешь жанр и отправляешь его мне, а я ищу интересный фильм это жанра.'
            self.bot.send_message(message.chat.id, mess1)
            mess2 = 'Давай начнем! Пришли мне номер какого-нибудь из этих жанров:\n\n1. Боевик\n2. Вестерн\n3. Военный\n4. Детектив\n5. Документальный\n6. Драма\n7. История\n8. Комедия\n9. Криминал\n10. Мелодрама\n11. Музыка\n12. Мультфильм\n13. Приключения\n14. Семейный\n15. Телефильм\n16. Триллер\n17. Ужасы\n18. Фантастика\n19. Фэнтези'
            answ = self.bot.send_message(message.chat.id, mess2)  # , reply_markup=markup
            self.bot.register_next_step_handler(answ, self.catch_genre_index)

        @self.bot.message_handler(content_types=['text'])
        def change_genre(message):
            print('catch')
            answ = self.bot.send_message(message.chat.id, 'Фильмы какого из этих жанров мне стоит поискать?\n\n1. Боевик\n2. Вестерн\n3. Военный\n4. Детектив\n5. Документальный\n6. Драма\n7. История\n8. Комедия\n9. Криминал\n10. Мелодрама\n11. Музыка\n12. Мультфильм\n13. Приключения\n14. Семейный\n15. Телефильм\n16. Триллер\n17. Ужасы\n18. Фантастика\n19. Фэнтези')
            self.bot.message_handler(answ, self.catch_genre_index)

    def catch_genre_index(self, message):
        try:
            print('try')
            index = int(message.text)
        except Exception as ex:
            print(ex)
            answ = self.bot.send_message(message.chat.id, 'Фильмы какого из этих жанров мне стоит поискать?\n\n1. Боевик\n2. Вестерн\n3. Военный\n4. Детектив\n5. Документальный\n6. Драма\n7. История\n8. Комедия\n9. Криминал\n10. Мелодрама\n11. Музыка\n12. Мультфильм\n13. Приключения\n14. Семейный\n15. Телефильм\n16. Триллер\n17. Ужасы\n18. Фантастика\n19. Фэнтези')
            self.bot.message_handler(answ, self.catch_genre_index)
            return
        id = message.chat.id
        a, b, c = self.parse_info(self.genres[index-1])
        self.send_information_to_make_a_post(a, b, c, id)

    def parse_info(self, selected_genre):
        seed(randint(0, 100))
        print(selected_genre)

        response = requests.get(f'https://api.themoviedb.org/3/discover/movie?api_key={self.api_key}&with_genres={selected_genre}&language={self.language}&page={randint(1, 2)}')
        response = json.loads(response.text)

        selected_film = randint(0, 19)
        print(response)
        self.title = response["results"][selected_film]["title"]
        self.genres = response["results"][selected_film]["genre_ids"]
        for i in range(len(self.genres)):
            self.genres[i] = self.genres_values[self.genres[i]]
        self.description = response["results"][selected_film]['overview']

        if self.title == "" or self.genres == [] or self.description == "":
            self.parse_info(selected_genre)
            return

        self.image = requests.get(f'https://image.tmdb.org/t/p/w500{response["results"][selected_film]["poster_path"]}').content
        print('nice')
        with open('image_for_post.jpg', 'wb') as file:
            file.write(self.image)

        return [self.title, self.genres, self.description]

    def send_information_to_make_a_post(self, title, genres, description, chat_id):
        formatted_genres = str(genres[0] + ', ') + ''.join(str(genres[i].lower() + ', ') for i in range(len(genres)) if i != 0)
        genres = formatted_genres[:-2]
        data = f'Название: {title}\n\nЖанры: {genres}\n\nОписание: {description}'
        self.bot.send_message(chat_id, data)
        with open("image_for_post.jpg", 'rb') as file:
            self.bot.send_document(chat_id, file)


if __name__ == '__main__':
    b = FilmsBot()
    b.bot.infinity_polling()
