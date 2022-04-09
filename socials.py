#
# Модуль SOCIALS.PY 
# определение базового класса "социальной сети"
# 

from io import TextIOWrapper
import os
import sys
from urllib import response
import requests

import abstract
from abstract import AbstractObject 

#
# Определение глобальных переменных и констант
#

#
# Глобальные функции модуля
#

class SocialNetwork(AbstractObject):

    # глобальные переменные класса
    token: str
    url: str

    # функция инициализация класса
    def __init__(self, url: str, token_file: str, log_file: TextIOWrapper) -> None:

        # вызываем конструктор родительского класса
        super().__init__()

        self.token = ''
        self.url = url
        self.log_file = log_file

        # загружаем токен из файла
        self.printlog(abstract.STATUS, 'Загружаем токен для работы с социальной сетью.')
        self.token = self.load_token_from_file(token_file)
        # если загрузить токен не удалось - завершаем программу
        if self.token == '':
            self.printlog(abstract.INFO, 'Токен не загружен! Работа программы остановлена!')
            sys.exit()

        return None

    # функция загрузки токена из файла
    def load_token_from_file(self, fname: str) -> str:

        # строка с токеном
        tokenname = ''
        # проверяем наличие файла для загрузки токена
        if os.path.isfile(fname):
            # открываем файл и считываем токен
            with open(fname, 'r', encoding='utf-8') as token_file:
                tokenname = token_file.readline().strip()
            if len(tokenname) == 0:
                self.printlog(abstract.ERROR, f'Не удалось загрузить токен из файла {fname}')
            else:
                self.printlog(abstract.OK, f'Токен из фалйа {fname} успешно загружен.')
        else:
            self.printlog(abstract.ERROR, f'Не найден токен файл {fname}')

        return tokenname
    
    # функция получения списка файлов для скачивания
    def get_photos_list(self) -> list:

        url_list = []

        return url_list

    # техническая функция получения списка файлов для скачивания
    def _get_file_list(self, url: str, headers: str, params: str) -> requests.Response:

        # обращаемся по указанному url
        response = requests.get(url, headers=headers, params=params)

        return response

    # функция скачивания файла по ссылке, не проверяет корректность переданного пути для сохранения
    def _download_file(self, url: str, headers: str, params: str, filename: str) -> requests.Response:

        # обращаемся по указанному url
        response = requests.get(url, headers=headers, params=params)
        # проверяем результат запроса
        if response.status_code != 200:
            return response
        # сохраняем файл
        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        return response
    
    # функция проверки существования папки для скаяивания
    # создает папку если она не существует
    def check_path(self, path) -> bool:

        # проверяем существование указанного пути 
        if not os.path.isdir(path):
            os.mkdir(path)

        return True

# end class SocialNetwork