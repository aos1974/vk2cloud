#
# Модуль APPS.PY 
# определение класса (объекта) типа "приложение"
# 

import configparser
import argparse
import os

#
# Определение глобальных переменных и констант
#

#
# Глобальные функции модуля
#

# класс основного приложения
class Application:

    # конфигурационные параметры приложения
    config: configparser.ConfigParser

    # функция инициализация класса
    def __init__(self, inifile: str) -> None:
        
        # инициализируем параметры приложения
        self.config = configparser.ConfigParser()
        # загружаем параметры приложения из файла, если задано имя файла
        if len(inifile) > 0:
            self.load_ini(inifile)

        return None

    # функция загрузки параметров приложения из файла
    def load_ini(self, inifile: str) -> bool:

         # проверяем наличие файла для загрузки
        if os.path.isfile(inifile):
            # загружаем параметры из файла
            self.config.read(inifile)

        return True
    
    # функция загрузки параметров приложения из командной строки
    def load_params(self) -> bool:

        return True
    
    # основная функция логики приложения 
    def run(self) -> None:

        return None

# end class