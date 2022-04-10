#
# Social Network Image Saver
# Основной модуль программы
#

from datetime import datetime
import json
import os
import shutil
import sys
from urllib import response
import argparse
import requests
from inputimeout import inputimeout, TimeoutOccurred

import abstract
from abstract import LogFileObject
import apps
from clouds import CloudStorage
from socials import SocialNetwork

#
# Определение глобальных переменных и констант
#

# файл с параметрами программы
INI_FILE = 'snis.ini'
# параметры ini файла
INI_SECTIONS = {'Main': 'Main', 'VK': 'VK', 'Yandex': 'YA'}
MAIN_SETTINGS = {'Social': 'SocialNetwork', 'Cloud': 'CloudDisk', 'Count': 'Count', 'Folder': 'DownloadFolder', 'Log': 'LogFile'}
VK_SETTINGS = {'URL': 'url', 'Token': 'TokenFile', 'ID': 'UserID'}
YANDEX_SETTINGS = {'URL': 'url', 'Token': 'TokenFile'}
# файл для сохранения данных о фотографиях
JSON_FILE = 'photos.json'

#
# Глобальные функции модуля
#

# создаем объект для соцсети Вконтакте
class SocialVK(SocialNetwork):

    # функция получения id пользователя ВКонтакте по его "имени" 
    def get_user_id(self, username: str) -> dict:

        user = {}

        # формируем параметры запроса
        url = self.url + 'users.get'
        headers = ''
        params = {'access_token': self.token, 'user_ids': username, 'v': '5.131'}
        # запрашиваем информацию о пользователе
        response = requests.get(url, headers=headers, params=params)
        # проверяем результат выполнения запроса
        if response.status_code != 200:
            self.printlog(abstract.ERROR, 'Запрос данных пользователя завершился с ошибкой!')
            self.printlog(abstract.ERROR, f'URL: {url}')
            self.printlog(abstract.ERROR, f'STATUS CODE: {response.status_code}')
            return user
        # если запрос выполнен успешно
        user = response.json()['response'][0]

        return user

    # переопределяем метод получения списка файлов, на специфичный для api Вконтакте
    def get_photos_list(self, owner_id: str, count: str) -> dict:
        
        url_list = {}
        url_list['count'] = 0
        url_list['img_list'] = []
        # формируем параметры запроса
        url = self.url + 'photos.get'
        headers = ''
        params = {'access_token': self.token, 'owner_id': owner_id, 'album_id': 'profile', 'extended': '1', 'photo_sizes': '1', 'v': '5.131'}
        # запрашиваем списко файлов с изображениями
        response = self._get_file_list(url, headers=headers, params=params)
        # проверяем результат выполнения запроса
        if response.status_code != 200:
            self.printlog(abstract.ERROR, 'Запрос списка фотографий завершился с ошибкой!')
            self.printlog(abstract.ERROR, f'URL: {url}')
            self.printlog(abstract.ERROR, f'STATUS CODE: {response.status_code}')
            return url_list
        # проверяем ответ api.vk на ошибки
        if 'error' in response.json():
            self.printlog(abstract.ERROR, 'Ответ на запрос фотографий вернулся с ошибкой')
            self.printlog(abstract.ERROR, 'Код ошибки: ' + str(response.json()['error']['error_code']) + ', Текст ошибки: ' + response.json()['error']['error_msg'])
            return url_list
        # обрабатываем список полученных файлов
        url_dict = response.json()['response']
        # если значение count не указано (пустое), то скачиваем все фотографии
        if len(count) == 0:
            cnt = url_dict.get('count')
        else:
            # если фотографий в альбоме меньше чем указано кол-во, то скачиваем все сколько есть 
            if int(count) > url_dict.get('count'):
                cnt = url_dict.get('count')
            else:
                cnt = int(count)
        # отбираем ссылки на фотографии кол-вом count, с максимальным разрешением
        self.printlog(abstract.OK, 'Получены ссылки на загрузку фотографий:')
        for img_url in url_dict.get('items'):
            rev_url_list = list(reversed(img_url.get('sizes')))
            rev_url_dict = dict(rev_url_list[0])
            url_list['img_list'].append(rev_url_dict)
            url_list['img_list'][url_list['count']]['likes'] = img_url['likes']['count']
            url_list['count'] += 1
            self.printlog(abstract.INFO, rev_url_dict.get('url'))
            if url_list['count'] == cnt:
                break

        return url_list
    
    # функция скачивания изображений из профиля ВКонтакте
    def download_photos(self, photos_list: dict, path: str) -> bool:

        headers = ''
        params = {'access_token': self.token, 'v': '5.131'}
        # проходим по всем ссылкам из списка
        for photo in photos_list['img_list']:
            url = photo['url']
            filename = photo['url'].split('/')
            filename = str(photo['likes']) + '-' + filename[len(filename)-1].strip()
            if filename.find('?') > 0:
                filename = filename[0:filename.find('?')]
            # сохраняем имя файла в словаре
            photo['filename'] = filename
            # формируем путь к файлу для загрузки
            filename = os.path.join(path, filename)
            response = self._download_file(url, headers, params, filename)
            # если были ошибки при загрузке фотографии
            if response.status_code != 200:
                self.printlog(abstract.ERROR, 'Загрузка фотографии завершилась с ошибкой!')
                self.printlog(abstract.ERROR, f'URL: {url}')
                self.printlog(abstract.ERROR, f'STATUS CODE: {response.status_code}')
                self.printlog(abstract.INFO, 'Работа программы завершена!')
                sys.exit()
            self.printlog(abstract.INFO, f'Файл {filename} сохраненн.')

        return True

# end class SocialVK

# создаем объект для соцсети Вконтакте
class YandexCloud(CloudStorage):

    # переопределяем функцию загрузки файлов из папки на компьютере
    def upload_files(self, folder: str) -> bool:
        
        # вызываем родительский объект
        if not super().upload_files(folder):
            return False
        
        # подготавливаем параметры подключения
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {self.token}'}

        # проверяем наличие папки для загрузки
        upload_folder = self._prepare_folder(folder)
        if not self._check_url_path(upload_folder, headers):
            return False

        # получаем список файлов для загруки из папки
        filelist = os.listdir(folder)
        # если папка пустая то загружать ничего не неужно
        if len(filelist) == 0:
            self.printlog(abstract.INFO, 'Нет файлов для загрузки!')
            return True
        # загружаем файлы в облако
        for f in filelist:
            path_2_file = os.path.join(folder, f)
            if os.path.isfile(path_2_file):
                if not self._upload_file(upload_folder, path_2_file, headers):
                    self.printlog(abstract.ERROR, f'Ошибка загрузки файла {path_2_file}')
                    return False
                self.printlog(abstract.INFO, f'Файл {path_2_file} загружен в облако!')

        return True

    # функция загрузки файла в облачное хранилище
    def _upload_file(self, upload_folder: str, fname: str, headers: str) -> bool:

        # формируем ссылку для загрузки файла
        params = {'path': fname, 'overwrite': 'true'}
        response = requests.get(self.url + '/' + 'upload', headers=headers, params=params)
        # если ошибка при получении линка для загрузки
        if response.status_code != 200:
            #print(Fore.RED + f'ERROR: ошибка формирования ссылки для загрузки!')
            return False
        # извлекаем ссылку для загрузки
        href = response.json().get('href', '')
    
        # проверяем наличие файла для загрузки
        if os.path.isfile(fname):
            # загружаем файл на ресурс
            response = requests.put(href, data=open(fname, 'rb'))
            # если ошибка при загрузке
            if response.status_code != 201:
                #print(Fore.RED + f'ERROR: ошибка загрузки файла на yandex.диск!')
                return False
        else:
            #print(Fore.RED + f'ERROR: файл {file} для загрузки не найден!')
            return False        

        return True

    # преобразуем путь к папке на ПК в папку для загрузки в облаке
    def _prepare_folder(self, folder: str) -> str:

        fld = []
        # проверяем наличие разделителей каталогов
        if folder.find('/') > 0:
            fld = folder.split('/')
        else: 
            fld.append(folder)
        
        if folder.find('\\') > 0:
            fld = folder.split('\\')
        else: 
            fld.append(folder)

        # выбираем последний элемент как имя папки в облаке
        fld = fld[-1]

        return fld

    # переопределяем функцию проверки существования в облаке папки для загрузки
    def _check_url_path(self, path: str, headers: str) -> bool:

        params = {'path': path, 'overwrite': 'true'}
        response = requests.get(self.url, headers=headers, params=params)
        if response.status_code == 404:
            # если папки не существует, то создаем ее
            response = requests.put(self.url, headers=headers, params=params)
        
        # если ошибка при обращении/создании папки на ресурсе 
        if not (response.status_code == 200 or response.status_code == 201):
            self.printlog(abstract.ERROR, f'Невозможно получить доступ к папке {path} в облачном хранилище!')
            self.printlog(abstract.ERROR, f'STATUS CODE: {response.status_code}')
            return False

        return True

# end class YandexCloud

# создаем объект нашего приложения 
class snisApplication(apps.Application):

    # объект социальная сеть, для скачивания фотографий
    socialnetwork: SocialNetwork
    cloud: CloudStorage

    # основная функция логики приложения
    def run(self, namespace: argparse.Namespace) -> str:

        # вызываем метод run() родительского класса
        run_status = super().run()
        # проверяем результаты работы родительского метода
        if run_status != 'OK':
            return run_status
        
        # обновляем из параметров запуска конфигурацию программы
        self.__update_snis_config(namespace)

        # начинаем вывод логов
        self.init_log()
        # выводим информацию о параметрах запуска программы
        self.about()

        # инициализируем объект соцсеть для доступа к фотографиям
        if self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social']) == INI_SECTIONS['VK']:
            # если в параметрах указана соцсеть Вконтаке
            self.printlog(abstract.INFO, 'Инициализируем подключение к сети ВКонтакте.')
            self.socialnetwork = SocialVK(self.config.get(INI_SECTIONS['VK'], VK_SETTINGS['URL']), self.config.get(INI_SECTIONS['VK'], VK_SETTINGS['Token']), self.log_file)
            # запрашиваем информацию о пользователе
            user = self.socialnetwork.get_user_id(self.config.get(INI_SECTIONS['VK'], VK_SETTINGS['ID']))
            # информация о пользователе ВКонтакте
            self.printlog(abstract.INFO, f'UserID: {user.get("id")}, UserName: {user.get("first_name") + " " + user.get("last_name")}')
            # получаем список файлов для загрузки
            self.printlog(abstract.STATUS, 'Запрашиваем список файлов для загрузки.')
            photos_list = self.socialnetwork.get_photos_list(user.get('id'), self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Count']))
        else:
            run_status = f"Неподдерживаемая соцсеть {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social'])}"
            self.printlog(abstract.ERROR, run_status)
            return run_status
        # проверяем каталог на ПК для загрузки фотографий, если нет то он создается
        folder = self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Folder'])
        self.printlog(abstract.STATUS, f'Загружаем фотографии в папку {folder} на компьютере.')
        self.socialnetwork.check_path(folder)
        # сохраняем изображения на локальный диск
        if not self.socialnetwork.download_photos(photos_list, folder):
            run_status = f'Невозможно сохранить изображения во временный каталог {os.path.join(os.getcwd(), folder)}'
            return run_status
        self.printlog(abstract.OK, 'Фотографии загружены на компьютер.')
        # сохраняем json файл с информацией о загруженных файлах
        if not self.save_json(photos_list, folder):
            run_status = f'Невозможно сохранить json файл во временный каталог {os.path.join(os.getcwd(), folder)}'
            return run_status
        # инициализируем объект облачное хранилище для загрузки фотографий
        if self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Cloud']) == INI_SECTIONS['Yandex']:
            # если в параметрах указан yandex.disk
            self.printlog(abstract.STATUS, 'Подключение к yandex.disk')
            self.cloud = YandexCloud(self.config.get(INI_SECTIONS['Yandex'], VK_SETTINGS['URL']), self.config.get(INI_SECTIONS['Yandex'], VK_SETTINGS['Token']), self.log_file)
        else:
            run_status = f"Неподдерживаемое облачное хранилище {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Cloud'])}"
            self.printlog(abstract.ERROR, run_status)
            return run_status
        
        # загружаем файлы из папки в облачное хранилище
        self.printlog(abstract.STATUS, f'Загружаем фотографии из папки {folder} в облачное хранилище.')
        if not self.cloud.upload_files(folder):
            run_status = f"Ошибка загрузки файлов в облачное хранилище"
            return run_status

        # Файлы успешно загружены в облако
        self.printlog(abstract.OK, 'Файлы успешно загружены в облако!')
        # удаление временной папки с фотографиями на ПК
        self.delete_local_photos(folder)
        # завершаем вывод логов
        self.stop_log()

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
        # --folder, наименование каталога для временных файлов
        if len(namespace.folder) > 0:
            self.update_config(INI_SECTIONS['Main'], MAIN_SETTINGS['Folder'], namespace.folder)
        # --log, имя log-файла, если не задано и нет в ini-файле, то лог не ведется
        if len(namespace.log) > 0:
            self.update_config(INI_SECTIONS['Main'], MAIN_SETTINGS['Log'], namespace.log)

        return True
    
    # функция сохранения данных о загруженных фотографиях в json файл
    def save_json(self, photos_list: dict, folder: str) -> bool:

        # фомируем имя json файла
        filename = os.path.join(folder, JSON_FILE)
        # формируем json dict для сохранения
        jlist = []
        for j in photos_list['img_list']:
            jlist.append({'file_name': j['filename'], 'size': j['type']})
        # открываем файл для записи
        with open(filename, 'w', encoding='utf-8') as jfile:
            json.dump(jlist, jfile)
        
        self.printlog(abstract.OK, f'JSON файл {filename} с информацией о загруженных фотографиях сохранен.')

        return True
    
    # инициализируем вывод сообщений/логгирование
    def init_log(self) -> None:

        # инициализируем объект для вывода сообщений
        if self.log_file == None:
            self.log_file = LogFileObject()
        # инициализируем вывод сообщений в файл
        self.log_file.open_log(self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Log']))
        # выводим сообщение о начале работы программы
        self.printlog(abstract.INFO, 'Начало работы программы: ' + datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

        return None 
    
    # функция удаления временной папки с фотографиями
    def delete_local_photos(self, folder) -> None:

        answer_list = ['ДА', 'Д', 'YES', 'Y']
        # запрос пользователю с ожиданием ответа 10 сек
        try:
            answer = inputimeout(prompt=f'Удалить времерную папку {folder} с загруженными фотографиями? [да/НЕТ] ', timeout=10)
        except TimeoutOccurred:
            answer = 'Нет'
            self.printlog(abstract.INFO, 'Сработал автоматический выбор [НЕТ]!')
        # удаляем каталог, если ответ утвердительный
        if answer.upper() in answer_list:
            shutil.rmtree(folder)
            self.printlog(abstract.INFO, f'Временный каталог {folder} удален.')

        return None

    # завершаем запись лога
    def stop_log(self) -> None:

        # выводим сообщение о завершении работы программы
        self.printlog(abstract.INFO, 'Программа завершила работу: ' + datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        # удаляем объект и вызываем его деструктор
        if self.log_file != None:
            del self.log_file

        return None
    
    # выводим информацию о параметрах запуска программы
    def about(self) -> None:

        # формируем строку для вывод а информации
        about_str = f'''Программа запущена со следующими парамертрами:
        -- {MAIN_SETTINGS['Social']} = {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social'])}
        -- {MAIN_SETTINGS['Cloud']} = {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Cloud'])}
        -- {MAIN_SETTINGS['Count']} = {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Count'])}
        -- {MAIN_SETTINGS['Folder']} = {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Folder'])}
        -- {MAIN_SETTINGS['Log']} = {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Log'])}
        '''
        self.printlog(abstract.INFO, about_str)

        return None

# end class snisApplication

# функция инициализации объекта парсинга командной строки
def createParser():

    # создаем объект парсинга командной строки
    parser = argparse.ArgumentParser()
    # добавляем аргументы командной строки
    # --file, имя ini-файла с параметрами программы (по умолчанию snis.ini)  
    # --count, кол-во фотографий для загрузки
    # --source, социальная сеть (по умолчанию определяется в ini файле)
    # --id, id (имя) пользователя соцсети
    # --folder, наименование каталога для временных файлов и папки в облачном хранилище
    # --log, имя log-файла, если не задано и нет в ini-файле, то лог не ведется
    parser.add_argument('--file', type=str, default=INI_FILE, help='имя ini-файла с параметрами программы (по умолчанию snis.ini)')
    parser.add_argument('--count', type=str, default= '', help='кол-во фотографий для загрузки (по умолчанию определяется в ini файле)')
    parser.add_argument('--source', type=str, default= '', help='социальная сеть (по умолчанию определяется в ini файле)')
    parser.add_argument('--id', type=str, default='', help='id (имя) пользователя соцсети')
    parser.add_argument('--folder', type=str, default='tmp', help='имя каталога для временных файлов и папки в облаке')
    parser.add_argument('--log', type=str, default='', help='имя log-файла, если не задано и нет в ini-файле, то лог не ведется')

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
