import telebot
from telebot import types

from random import randint, seed

import json

import requests


class TeleBot:
    def __init__(self):
        self.bot = telebot.TeleBot('5049347663:AAHrg7oBpxXO_w5oeWaptAINCbkCKNojdYo')
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
        self.only_genres_keys = [28, 37, 10752, 9648, 99, 18, 36, 35, 80, 10749, 10402, 16, 12, 10751, 10770, 53, 27, 878, 14]

        self.api_key = '51201bea16768dcaccd8a5c90e6c7972'
        self.language = 'ru-RU'

        self.current_genre = None

        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            self.select_genre(message)

    def select_genre(self, message):
        answ = self.bot.send_message(message.chat.id, 'Фильмы какого из этих жанров мне стоит поискать?\n\n1. Боевик\n2. Вестерн\n3. Военный\n4. Детектив\n5. Документальный\n6. Драма\n7. История\n8. Комедия\n9. Криминал\n10. Мелодрама\n11. Музыка\n12. Мультфильм\n13. Приключения\n14. Семейный\n15. Телефильм\n16. Триллер\n17. Ужасы\n18. Фантастика\n19. Фэнтези', reply_markup=types.ReplyKeyboardRemove())
        self.bot.register_next_step_handler(answ, self.analyze_genre)

    def analyze_genre(self, message):
        index = int(message.text)
        self.current_genre = self.only_genres_keys[index-1]
        title, genre, description = self.find_film(self.current_genre)
        self.send_results(message.chat.id, title, genre, description)

    def send_results(self, chat_id, title, genres, description):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        next_film = types.KeyboardButton('Следующий')
        change_genre = types.KeyboardButton('Сменить жанр')
        markup.add(change_genre, next_film)

        formatted_genres = str(genres[0] + ', ') + ''.join(str(genres[i].lower() + ', ') for i in range(len(genres)) if i != 0)
        genres = formatted_genres[:-2]
        data = f'Название: {title}\n\nЖанры: {genres}\n\nОписание: {description}'
        self.bot.send_message(chat_id, data)
        with open("image_for_post.jpg", 'rb') as file:
            answ = self.bot.send_document(chat_id, file, reply_markup=markup)
        self.bot.register_next_step_handler(answ, self.next_step_after_film)

    def find_film(self, selected_genre):
        seed(randint(0, 100))
        print(selected_genre)

        response = requests.get(f'https://api.themoviedb.org/3/discover/movie?api_key={self.api_key}&with_genres={selected_genre}&language={self.language}&page={randint(1, 20)}')
        response = json.loads(response.text)

        selected_film = randint(0, 19)
        self.title = response["results"][selected_film]["title"]
        self.genres = response["results"][selected_film]["genre_ids"]
        for i in range(len(self.genres)):
            self.genres[i] = self.genres_values[self.genres[i]]
        self.description = response["results"][selected_film]['overview']

        if self.title == "" or self.genres == [] or self.description == "":
            self.find_film(selected_genre)
            return

        self.image = requests.get(f'https://image.tmdb.org/t/p/w500{response["results"][selected_film]["poster_path"]}').content
        print('nice')
        with open('image_for_post.jpg', 'wb') as file:
            file.write(self.image)

        return [self.title, self.genres, self.description]

    def next_step_after_film(self, message):
        print('******', message.text, '******')
        if message.text == 'Следующий':
            title, genre, description = self.find_film(self.current_genre)
            self.send_results(message.chat.id, title, genre, description)
            return
        if message.text == 'Сменить жанр':
            self.select_genre(message)
        else:
            answ = self.bot.send_message(message.chat.id, 'Упс... Я пока не знаю такой команды:(\nПопробуй выбрать действие из предложенных ниже')
            self.bot.register_next_step_handler(answ, self.next_step_after_film)


if __name__ == '__main__':
    client = TeleBot()
    client.bot.infinity_polling()
