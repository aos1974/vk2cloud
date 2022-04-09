#
# Модуль ABSTRACT.PY 
# определение базового класса для всех объектов проекта
# определение класса для вывода информации в лог файл
# 

import colorama
from colorama import Fore
from io import TextIOWrapper

#
# Определение глобальных переменных и констант
#

ERROR = '[Ошибка]'
INFO = '[Информация]'
STATUS = '[Статус]'
OK = '[OK]'

#
# Глобальные функции модуля
#

# объект для вывода событий на экран и/или в файл
class LogFileObject:

    # глобальные переменные класса
    log_to_screan: bool
    log_to_file: bool
    log_file_opened: bool
    log_file_name: str
    log_file: TextIOWrapper

    # функция инициализации класса
    def __init__(self) -> None:
        
        # по умолчанию вывод событий на экран включен
        self.log_to_screan = True
        # вывод событий в файл по умолчанию выключен
        self.log_to_file = False
        self.log_file_opened = False
        self.log_file_name = ''

        return None
    
    # инициализация файла для записи лога
    def open_log(self, filename: str) -> bool:

        # открываем для дозаписи лог-файл
        self.log_file = open(filename, 'a', encoding='utf-8')
        # настраиваем внутренние переменные
        self.log_to_file = True
        self.log_file_opened = True
        self.log_file_name = filename

        return True
    
    # вывод сообщений о событиях класса
    def print_log(self, status: str, log_strint: str) -> None:

        # если разрешен вывод на экран
        if self.log_to_screan:
            # в зависимости от статуса сообщения оно выводится в цвете
            if status == ERROR:
                print(Fore.RED + '', end='')
            elif status == INFO:
                print(Fore.BLUE + '', end='')
            elif status == STATUS:
                print(Fore.YELLOW + '', end='')
            elif status == OK:
                print(Fore.GREEN + '', end='')
            else:
                print(Fore.WHITE + '', end='')

            print(status + ' ' + log_strint)
            # возвращаем цвет сообщений по умолчанию (белый)
            print(Fore.WHITE + '', end='')

        # если разрешен вывод в файл
        if self.log_to_file:
            # если файл открыт, то выводим сообщения в файл
            if self.log_file_opened:
                self.log_file.write(status + ' ' + log_strint + '\n')

        return None

    # закрываем лог файл 
    def close_log(self) -> bool:

        # если файл открыт для записи, то закрываем его
        if self.log_file_opened:
            self.log_file.close()
        # вывод событий в файл выключен
        self.log_to_file = False
        self.log_file_opened = False
        self.log_file_name = ''

        return True
    
    # деструктор класса
    def __del__(self) -> None:

        # закрываем открытый файл
        self.close_log()

        return None

# end class LogFileObject

# родительский объект для всех классов проекта
class AbstractObject:

    log_file: LogFileObject
    
    # функция инициализации класса
    def __init__(self) -> None:

        self.log_file = None

        return None

    # функция вывода сообщений
    def printlog(self, status: str, log_string: str) -> None:

        # если объект не инициализирован
        if self.log_file == None:
            return None
        # выводим сообщения
        self.log_file.print_log(status, log_string)

        return None

# end class AbstractObject
