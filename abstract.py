#
# Модуль ABSTRACT.PY 
# определение базового класса для всех объектов проекта
# 

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
    
    # инициализация файла для записи лога работы
    def open_log(self, filename: str) -> bool:

        return True
    
    # вывод сообщений о событиях класса
    def print_log(self, status: str, log_strint: str):

        return None

    # закрываем лог файл 
    def close_log(self) -> bool:

        return True
    
    # деструктор класса
    def __del__(self) -> None:

        return None

# end class LogFileObject

# родительский объект для всех классов проекта
class AbstractObject:

    log_file: LogFileObject
    
    # функция инициализации класса
    def __init__(self) -> None:
        pass

    # функция вывода сообщений
    def printlog(self, status: str, log_string: str) -> None:

        # если объект не инициализирован
        if self.log_file == None:
            return None
        # выводим сообщения
        self.log_file.print_log(status, log_string)

        return None

# end class AbstractObject

f = open('snis.ini', 'r')
print(type(f))