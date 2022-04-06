#
# Social Network Image Saver
# Основной модуль программы
#

import os
import sys
from urllib import response
import apps
import argparse
import requests

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
            return url_list
        # проверяем ответ api.vk на ошибки
        if 'error' in response.json():
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
        for img_url in url_dict.get('items'):
            rev_url_list = list(reversed(img_url.get('sizes')))
            rev_url_dict = dict(rev_url_list[0])
            url_list['img_list'].append(rev_url_dict)
            url_list['img_list'][url_list['count']]['likes'] = img_url['likes']['count']
            url_list['count'] += 1
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
            filename = os.path.join(path, filename)
            if filename.find('?') > 0:
                filename = filename[0:filename.find('?')]
            response = self._download_file(url, headers, params, filename)

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
            return True
        # загружаем файлы в облако
        for f in filelist:
            path_2_file = os.path.join(folder, f)
            if os.path.isfile(path_2_file):
                if not self._upload_file(upload_folder, path_2_file, headers):
                    return False

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
            #print(Fore.RED + f'ERROR: ошибка обращения к {url}!')
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

        # инициализируем объект соцсеть для доступа к фотографиям
        if self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social']) == INI_SECTIONS['VK']:
            # если в параметрах указана соцсеть Вконтаке
            self.socialnetwork = SocialVK(self.config.get(INI_SECTIONS['VK'], VK_SETTINGS['URL']), self.config.get(INI_SECTIONS['VK'], VK_SETTINGS['Token']))
            # запрашиваем информацию о пользователе
            user = self.socialnetwork.get_user_id(self.config.get(INI_SECTIONS['VK'], VK_SETTINGS['ID']))
            # можно вывести информацию о пользователе
            # print(user.get('fires_name') + ' ' + user.get(''last_name))
            # получаем список файлов для загрузки
            photos_list = self.socialnetwork.get_photos_list(user.get('id'), self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Count']))
        else:
            run_status = f"Неподдерживаемая соцсеть {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Social'])}"
            return run_status
        # проверяем каталог на ПК для загрузки фотографий, если нет то он создается
        folder = self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Folder'])
        self.socialnetwork.check_path(folder)
        # сохраняем изображения на локальный диск
        if not self.socialnetwork.download_photos(photos_list, folder):
            run_status = f'Невозможно сохранить изображения во временный каталог {os.path.join(os.getcwd(), folder)}'
            return run_status

        # инициализируем объект облачное хранилище для загрузки фотографий
        if self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Cloud']) == INI_SECTIONS['Yandex']:
            # если в параметрах указан yandex.disk
            self.cloud = YandexCloud(self.config.get(INI_SECTIONS['Yandex'], VK_SETTINGS['URL']), self.config.get(INI_SECTIONS['Yandex'], VK_SETTINGS['Token']))
        else:
            run_status = f"Неподдерживаемое облачное хранилище {self.config.get(INI_SECTIONS['Main'], MAIN_SETTINGS['Cloud'])}"
            return run_status
        
        # загружаем файлы из папки в облачное хранилище

        if not self.cloud.upload_files(folder):
            run_status = f"Ошибка загрузки файлов в облачное хранилище"
            return run_status

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
