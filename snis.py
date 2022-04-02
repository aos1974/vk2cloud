#
# Social Network Image Saver
# Основной модуль программы
#

import sys
import apps
import argparse

from socials import SocialNetwork

#
# Определение глобальных переменных и констант
#

# файл с параметрами программы
INI_FILE = 'snis.ini'
# параметры ini файла
INI_SECTIONS = {'Main': 'Main', 'VK': 'VK', 'Yandex': 'YA'}
MAIN_SETTINGS = {'Social': 'SocialNetwork', 'Cloud': 'CloudDisk', 'Count': 'Count'}
VK_SETTINGS = {'URL': 'url', 'Token': 'TokenFile', 'ID': 'UserID'}
YANDEX_SETTINGS = {'URL': 'url', 'Token': 'TokenFile'}

#
# Глобальные функции модуля
#

class snisApplication(apps.Application):

    # объект социальная сеть, для скачивания фотографий
    socialnetwork: SocialNetwork

    # основная функция логики приложения
    def run(self, namespace: argparse.Namespace) -> str:

        # вызываем метод run() родительского класса
        run_status = super().run()
        # проверяем результаты работы родительского метода
        if run_status != 'OK':
            return run_status
        
        # обновляем из параметров запуска конфигурацию программы
        self.__update_snis_config(namespace)

        # инициализируем объект соцсеть для доступа к фотографиям
        if self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social']) == INI_SECTIONS['VK']:
            # если в параметрах указана соцсеть Вконтаке
            pass
        else:
            run_status = f"Неподдерживаемая соцсеть {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social'])}"

        return run_status
    
    # обновление из параметров запуска конфигурации программы
    def __update_snis_config(self, namespace: argparse.Namespace) -> bool:

        # --count, кол-во фотографий для загрузки
        if len(namespace.count) > 0:
            self.update_config(INI_SECTIONS['Main'], MAIN_SETTINGS['Count'], namespace.count)
        # --source, социальная сеть для загрузки
        if len(namespace.source) > 0:
            self.update_config(INI_SECTIONS['Main'], MAIN_SETTINGS['Social'], namespace.source)
        # --id, id (имя) пользователя соцсети
        if len(namespace.id) > 0:
            # проверяем наличии группы параметров конфигурации
            if namespace.source.upper() in self.config.sections():
                self.update_config(namespace.source.upper(), 'UserID', namespace.id)

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
    parser.add_argument('--count', type=str, default= '', help='кол-во фотографий для загрузки (по умолчанию определяется в ini файле)')
    parser.add_argument('--source', type=str, default= '', help='социальная сеть (по умолчанию определяется в ini файле)')
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
