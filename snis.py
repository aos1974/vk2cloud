#
# Social Network Image Saver
# Основной модуль программы
#

import sys
import apps
import argparse

#
# Определение глобальных переменных и констант
#

# файл с параметрами программы
INI_FILE = 'snis.ini'

#
# Глобальные функции модуля
#

class snisApplication(apps.Application):

    # основная функция логики приложения
    def run(self, namespace: argparse.Namespace) -> str:

        # вызываем метод run() родительского класса
        run_status = super().run()
        # проверяем результаты работы родительского метода
        if run_status != 'OK':
            return run_status
        
        # обновляем из параметров запуска конфигурацию программы
        self.__update_snis_config(namespace)

        return run_status
    
    # обновление из параметров запуска конфигурации программы
    def __update_snis_config(self, namespace: argparse.Namespace):

        # --count, кол-во фотографий для загрузки
        if len(namespace.count) > 0:
            self.update_config('Main', 'Count', namespace.count)
        # --source, социальная сеть для загрузки
        if len(namespace.source) > 0:
            self.update_config('Main', 'SocialNetwork', namespace.source)
        # --id, id (имя) пользователя соцсети
        if len(namespace.id) > 0:
            # проверяем наличии группы параметров конфигурации
            if namespace.source() not in self.config.sections():

        return True


# end class snisApplication

# функция инициализации объекта парсинга командной строки
def createParser():

    # создаем объект парсинга командной строки
    parser = argparse.ArgumentParser()
    # добавляем аргументы командной строки
    # --file, имя ini-файла с параметрами программы (по умолчанию snis.ini)  
    # --count, кол-во фотографий для загрузки
    # --id, id (имя) пользователя соцсети
    parser.add_argument('--file', type=str, default=INI_FILE, help='имя ini-файла с параметрами программы (по умолчанию snis.ini)')
    parser.add_argument('--count', type=str, help='кол-во фотографий для загрузки (по умолчанию 5)')
    parser.add_argument('--source', type=str, help='социальная сеть (по умолчанию VK)')
    parser.add_argument('--id', type=str, default='', help='id (имя) пользователя соцсети')

    return parser

#
# Главная функция программы
#

def main() -> None:

    # создаем объект парсинга командной строки
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    
    # инициализируем объект приложения программы
    snisApp = snisApplication(namespace.file)
    # запускаем основной обработчик приложения
    result = snisApp.run(namespace)
    if result == 'OK':
        print('УСПЕХ: Резервная копия фотографий сделана!')
    else:
        print(f'ПРОБЛЕМА: {result}')

    return None
#
# Основная программа
#

if __name__ == '__main__':
    main()
