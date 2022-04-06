#
# Модуль CLOUDS.PY 
# определение базового класса "облачного хранилища"
# 

import os

#
# Определение глобальных переменных и констант
#

#
# Глобальные функции модуля
#

class CloudStorage:

    # глобальные переменные класса
    token: str
    url: str

    # функция инициализация класса
    def __init__(self, url: str, token_file: str) -> None:
        
        self.token = ''
        self.url = url

        # загружаем токен из файла
        self.token = self.load_token_from_file(token_file)

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
