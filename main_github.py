# 1. Создаем объет Пользователь соц. сети USER_SocNet -
# (имя соц.сети и ID пользователя)
# 2. Создаем метод сохранить фото в хранилище:
# (имя хранилища, токен и название папки)
# 2.1 Признаки фоток заданы
# 2.2 Отчет о переносе фоток в JSON формате в файл сохранить
# в папку и вывести на экран
# 2.3 Прогресс-бар процесса загрузки

import time
import json
import requests
from pprint import pprint


# Print iterations progress
def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1,\
    length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)

    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# Документация по API VK: https://vk.com/dev

# константы: названия соц. сетей
SOCIAL_NET_VK = 'VK' # ВКонтаке
SOCIAL_NET_OK = 'OK' # Одноклассники
SOCIAL_NET_IG = 'IG' # Инстаграмм
SOCIAL_NET_FB = 'FB' # Фейсбук

#Облачные хранилища
YANDEX_DISK = 'YD' # Яндекс.Диск
GOOGLE_DRIVE = 'GD' # Гугл.Диск

class UserSocNet:
    """
    Класс - пользователь социальной сети

    """

    # Префикс доступа к профилю VK:
    PROFILE_VK_URL = 'https://vk.com/id'
    # Адрес API-сервиса VK: api.vk.com/method
    API_VK_URL = 'https://api.vk.com/method'
    # Метод получения фотографий
    VK_METHOD_PHOTOS_GET='/photos.get'
     # Метод получения инфо о пользователе:
    VK_METHOD_USERS_GET='/users.get'

    def __init__(self, soc_net_name, token, user_id_or_name) -> None:
        self.soc_net_name = soc_net_name
        self.token = token
        self.user_id_or_name = user_id_or_name

        if isinstance(self.user_id_or_name,int):
            self.user_id = self.user_id_or_name
        else:
            self.user_id = self.get_user_ID_by_user_name(self.user_id_or_name)

    # получить ID пользователя, при необходимости:

    def get_user_ID_by_user_name(self, user_name):
        """
        Получить ID пользователя по его имени
        :param user_name:
        :return:
        """
        ID = -1

        if self.soc_net_name == SOCIAL_NET_VK:
            #запрос
            response = requests.get(
                self.API_VK_URL + self.VK_METHOD_USERS_GET,
                params={
                    'access_token': self.token,
                    'user_ids': user_name,
                    'v': 5.21
                }
            )
        else:
            print('Не найден API соц. сети!')
            return ID

        # проверка на error: есть ли в ответе ключ "error"
        if response.json().get('error'):
            print(f"Ошибка: {response.json()['error']['error_code']}")
            return ID
        else:
            ID = response.json()['response'][0]['id']

        return ID


    def get_photo (self, num_photos=5) -> list:
        """
        Получаем список из num_photos фотографий в виде списка
        По умолчанию - первых 5 фото
        :return:

        """
        album = []

        if self.soc_net_name == SOCIAL_NET_VK:
        # запрос в ВКонтакте
            response = requests.get(
                self.API_VK_URL + self.VK_METHOD_PHOTOS_GET,
                params={
                    'access_token': self.token,
                    'owner-id': self.user_id,
                    'album_id': 'profile',
                    'rev': 0,
                    'extended': 1, # дополнительные поля
                    'feed_type':'photo',
                    'photo_sizes':1, # возвращает доступные размеры фото в специальном формате, см.  https://vk.com/dev/objects/photo_sizes
                    'offset': 0,
                    'count':num_photos,
                    'v': 5.21
                }
            )

        else:
            print('Не найден API соц. сети!')
            return album

        # проверка на error: есть ли в ответе ключ "error"
        if response.json().get('error'):
            print (f"Ошибка: {response.json()['error']['error_code']}")
            return album
        else:
            answer=response.json()['response']['items']
            #pprint(answer)

        # формируем список фото максимального размера
        for i,next_photo in enumerate(answer):
            photo = dict()
            photo['id']=next_photo['id']
            photo['date'] = next_photo['date'] # в секундах, начиная с эпохи (time.ctime)
            photo['likes'] = next_photo['likes']['count']
            # ищем крайний  - он же максимальный - размер
            num_sizes = len(next_photo['sizes'])
            photo['size'] = next_photo['sizes'][num_sizes-1]['type']
            photo['src'] = next_photo['sizes'][num_sizes-1]['src']

            # расширение файла
            src_list = photo['src'].split('.')
            photo['file_ext'] = src_list[len(src_list)-1]

            # переводим дату в "нормальный формат"
            date = time.gmtime(photo['date'])
            photo['file_name'] = 'VK_Photo(' + str(i) + ')-' + str(photo['likes']) + 'likes-'\
                    + str(date.tm_mday) + '.'\
                    + str(date.tm_mon) + '.'\
                    + str(date.tm_year)

            #next_photo_key='photo-' + str(i+1)
            album.append(photo)


        return album


    def save_file_to(self, store_name, token, list_info, num_photos, folder_name='') -> dict:
        """
        Сохраняем файлы на диск в облаке в указанную папку. Источник файлов описан в json_info
        :param store_name:
        :param token:
        :param json_info:
        :param folder_name:
        :return:

        """

        #token = ''
        token_prefix = 'OAuth'
        METHOD_GET = 'GET'
        METHOD_PUT = 'PUT'
        METHOD_POST = 'POST'
        API_YD_URL = 'https://cloud-api.yandex.net:443'
        YD_RESOURCE_UPLOAD = '/v1/disk/resources/upload'  # Загрузка файла на диск по URL
        YD_RESOURCE_CREATE_FOLDER = '/v1/disk/resources'  # Загрузка файла на диск по URL
        headers = {'Authorization': f'{token_prefix} {token}'}

        # работаем с Yandex
        if store_name == YANDEX_DISK:
            # json-отчет
            report=dict()
            report['info']='Загрузка файлов на Yandex.Disk'
            report['folder'] = folder_name
            report['files'] = []

            if folder_name != '':
                # создаем папку
                params = {'path': f'/{folder_name}'}
                # делаем запрос
                response = requests.request(METHOD_PUT, API_YD_URL + YD_RESOURCE_CREATE_FOLDER, params=params, headers=headers)
                resp_json = response.json()

                # проверка на error: есть ли в ответе ключ "error"
                if resp_json.get('error'):
                    print(f"Ошибка создания папки: {resp_json['message']}")
                    return report

            # закачиваем файлы
            num_files = len(list_info)
            # Инициируем прогресс-бар
            print_progress_bar(0, num_files, prefix='Процесс загрузки файлов:', suffix='Завершено', length=50)
            for i,file in enumerate(list_info):

                if i == num_photos:
                    break

                operation_rep=dict()
                file_name=file['file_name'] + '.' + file['file_ext']
                file_url=file['src']

                if folder_name == '':
                    params = {'path': f'/{file_name}', 'url': file_url}
                else:
                    params = {'path':f'/{folder_name}/{file_name}', 'url':file_url}
                # закачиваем файл на диск
                response = requests.request(METHOD_POST, API_YD_URL + YD_RESOURCE_UPLOAD, params=params, headers=headers)
                resp_json = response.json()

                # проверка на error: есть ли в ответе ключ "error"
                if resp_json.get('error'):
                    print(f"Ошибка загрузки файла: {resp_json['message']}")
                    return report

                operation_rep['file_name']=file_name
                operation_rep['size'] = file['size']
                print_progress_bar(i+1, num_files, prefix='Процесс загрузки файлов:', suffix='Завершено', length=50)

                # запись в отчет
                report['files'].append(operation_rep)

            # записываем отчет в файл в текущую директорию: имя файла = report.json
            with open("report.json","w") as f:
                json.dump(report,f,ensure_ascii=False, indent=2)

        return report


    def __str__(self) -> str:
        """
        Определяет поведение функции str(), вызванной для экземпляра класса User_SocNet.
        Для использования в print()

        :return:
        """
        return (str(f'Пользователь сети {self.soc_net_name}\
            {self.PROFILE_VK_URL+str(self.user_id)}. {self.__dict__}. {self.__class__}'))



def main():
    # -----------------------------------------------------------------
    # owner_id = 1 (Павел Дуров)
    # получаем Username или ID пользователя VK:

    social_net_data = input('Выберите название социальной сети\n\
        <ВКонтакте - 1,\n\
        Одноклассники - 2 ( ** В данной версии недоступно! **),\n\
        Instagram - 3 ( ** В данной версии недоступно! **)\n\
        Facebook - 4 ( ** В данной версии недоступно! **)>: ')

    if not social_net_data.isdigit():
        print('\nВы ввели некорреткное название соц.сети!')
        return -1
    else:

        if int(social_net_data) == 1:
            social_net_name = SOCIAL_NET_VK
        #elif int(social_net_data) == 2:
        #   social_net_name = SOCIAL_NET_OK
        #elif int(social_net_data) == 3:
        #   social_net_name = SOCIAL_NET_IG
        #elif int(social_net_data) == 4:
        #   social_net_name = SOCIAL_NET_FB
        else:
            print('\nВы ввели некорреткное название соц.сети!')
            return -1


    user_data = input('Введите идентификатор пользователя (ID) или его короткое имя: ')
    token = input('Введите токен для доступа к API соц. сети: ')

    user_vk = UserSocNet(social_net_name, token, user_data)
    print('\n******************************************************')
    print(user_vk)

    album = user_vk.get_photo(8)
    print(type(album))
    print(f'Найдено {len(album)} фотографий')
    # pprint(album)


    # -----------------------------------------------------------------
    sky_data = input('Выберите облачный ресурс для хранения фото\n\
         <Яндекс.Диск - 1,\n\
         Google.Drive - 2 ( ** В данной версии недоступно! **)>: ')

    if not sky_data.isdigit():
        print('\nВы ввели некорреткное название хранилища!')
        return (-1)
    else:
        if int(sky_data) == 1:
            disk_net_name = YANDEX_DISK
        # elif int(sky_data) == 2:
        #   disk_net_name = GOOGLE_DRIVE
        else:
            print('\nВы ввели некорреткное название хранилища!')
            return (-1)

    folder_name = input('Введите наименование папки: ')
    token = input('Введите токен для доступа к хранилищу: ')
    num_photos = input(f'Введите количество фото для сохранения в хранилище (от 0 до {len(album)}): ')

    if (not num_photos.isdigit() or ((int(num_photos) < 0) and (int(num_photos) > len(album)))):
        print('\nВы ввели некорреткное количество фото!')
        return -2

    res = user_vk.save_file_to(disk_net_name, token, album, int(num_photos), folder_name)
    print('\nОтчет (продублирован на диске в файле report.json):')
    pprint(res)

if __name__ == '__main__':
    main()

