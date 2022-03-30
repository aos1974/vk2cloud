#
# Модуль APPS.PY 
# определение базового класса "приложение"
# 

import configparser
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
        else:
            self.update_config('STATUS', 'LOAD_INI', 'FAILED')

        return None

    # функция загрузки параметров приложения из файла
    def load_ini(self, inifile: str) -> bool:

         # проверяем наличие файла для загрузки
        if os.path.isfile(inifile):
            # загружаем параметры из файла
            self.config.read(inifile)
            self.update_config('STATUS', 'LOAD_INI', 'OK')
        else:
            self.update_config('STATUS', 'LOAD_INI', 'FAILED')
            return False

        return True
    
    # обновление конфигурационных параметров прилолжения
    def update_config(self, section: str, setting: str, value: str) -> bool:

        # проверяем наличии группы параметров конфигурации
        if section not in self.config.sections():
            # если такой груупы нет, тогда создаем ее с параметрами
            self.config[section] = {setting: value}
        else:
            # проверяем наличие параметра в секции
            if setting not in self.config.set:
                # создаем параметр со значением
                self.config.set[section] = {setting: value}
            else:
                # обновляем значение параметра
                self.config.set(section, setting, value)

        return True
    
    # основная функция логики приложения 
    def run(self) -> str:

        run_status = 'OK'

        # проверяем статус загрузки ini-файла (параметров приложения)
        if self.config['STATUS']['LOAD_INI'] != 'OK':
            run_status = 'Ошибка загрузки INI-файла!'

        return run_status

# end class