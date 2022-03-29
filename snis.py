#
# Social Network Image Saver
# Основной модуль программы
#

import apps

#
# Определение глобальных переменных и констант
#

# файл с параметрами программы
INI_FILE = 'snis.ini'

#
# Глобальные функции модуля
#

#
# Главная функция программы
#

def main():

    snisApp = apps.Application(INI_FILE)
    snisApp.run()

    print(snisApp.config['Main']['SocialNetwork'])

    return None
#
# Основная программа
#

if __name__ == '__main__':
    main()
