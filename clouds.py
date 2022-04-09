#
# Модуль CLOUDS.PY 
# определение базового класса "облачного хранилища"
# 

import os
from io import TextIOWrapper
import sys

import abstract
from abstract import AbstractObject

#
# Определение глобальных переменных и констант
#

#
# Глобальные функции модуля
#

class CloudStorage(AbstractObject):

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

    # функция загрузки файла в облачное хранилище
    def _upload_file(self, fname: str) -> bool:

        return True

    # функция проверки существования в облаке папки для загрузки
    def _check_url_path(self, path: str) -> bool:

        return True
    
    # функция загрузки файлов из папки на компьютере
    def upload_files(self, path: str) -> bool:

        return True

# end class CloudStorage
