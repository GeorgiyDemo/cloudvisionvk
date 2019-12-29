#TODO Чёрный шрифт, когда изображение преимущественно белое
#TODO Белый шрифт, когда изображение преимущественно черное

import vk_api
import yaml
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import requests
import imageprocessing

TTF_DIR = "./MuseoSansCyrl-300.ttf"
group_id = 175867271

#TODO id сообщества в yaml
#TODO путь TTF в yaml
def get_settings():
    """
        Чтение токена vk с файла yaml
    """
    with open("./token.yaml", 'r') as stream:
        return yaml.safe_load(stream)


class VkProcessing():
    def __init__(self, vk, user_id, path, message):

        self.path = path
        self.message = message
        self.user_id = user_id
        self.vk = vk

        if message == {}:
            self.vk.method('messages.send', {'user_id': self.user_id, 'random_id': get_random_id(),
                                             'message': "Нет результатов для этого фото\nПопробуй другое 👀"})
        else:

            # Загрузка фото
            self.photo_uploader()

            # Отправка сообщения
            self.message_sender()

    def photo_uploader(self):
        """
        Метод для загрузки фото с локали в VK
        """

        server_url = self.vk.method('photos.getMessagesUploadServer', {'peer_id': self.user_id})["upload_url"]
        photo_r = requests.post(server_url, files={'photo': open(self.path, 'rb')}).json()
        photo_final = self.vk.method("photos.saveMessagesPhoto",
                                     {"photo": photo_r["photo"], "server": photo_r["server"], "hash": photo_r["hash"]})[
            0]
        photo_str = "photo" + str(photo_final["owner_id"]) + "_" + str(photo_final["id"])
        self.photo_str = photo_str

    def message_sender(self):
        """
        Отправка сообщения пользователю VK
        """
        objects_dict = self.message

        out_str = ""
        for key, value in objects_dict.items():
            out_str += key + " " + str(int(round(value, 2) * 100)) + "%\n"

        self.vk.method('messages.send', {
            'user_id': self.user_id,
            'random_id': get_random_id(),
            'message': 'Ваши результаты:\n' + out_str,
            'attachment': self.photo_str}
                       )

class MainClass():
    def __init__(self):

        # Авторизуемся как сообщество
        self.vk = vk_api.VkApi(token=get_settings())
        self.processing()

    def get_url(self, message_id):
        """
        Метод для получения url изобржения из id сообщения
        """
        
        # Получаем сообщеньку по методу
        r = self.vk.method('messages.getById', {'message_ids': message_id, "group_id" : group_id})["items"]
        
        # Находим все размеры фото
        all_sizes = r[0]["attachments"][0]["photo"]["sizes"]

        # В цикле по каждой ищем самое большое изображение
        height, width, index = 0, 0, 0
        for i in range(len(all_sizes)):
            if all_sizes[i]["width"] > width and all_sizes[i]["height"] > height:
                height = all_sizes[i]["height"]
                width = all_sizes[i]["width"]
                index = i

        # Обращаемся к полученному индексу
        url = all_sizes[index]["url"]

        # Берем последний элемент списка (т.к. он самый большой)
        return url

    def processing(self):
        """
        Метод обработки входящих сообщений
        """
        # Работа с сообщениями
        longpoll = VkLongPoll(self.vk)

        # Основной цикл
        for event in longpoll.listen():

            # Если пришло новое сообщение
            if event.type == VkEventType.MESSAGE_NEW:

                # Если оно имеет метку для бота
                if event.to_me:

                    if event.text == "Начать":
                        self.vk.method('messages.send', {'user_id': event.user_id, 'random_id': get_random_id(),
                                             'message': "Привет, просто отправь мне любое фото 🧩"})

                    else:
                        msg_id = event.message_id

                        attachments = event.attachments
                        #Если пришло фото
                        if attachments != {} and attachments["attach1_type"] == "photo":
                            #Получаем url изображения
                            url = self.get_url(msg_id)
                            #Передаем url модулю-обработчику фото
                            detector = imageprocessing.PhotoProcessing(url, TTF_DIR)
                            #Отправляем результаты пользователю
                            VkProcessing(self.vk, event.user_id, detector.path, detector.results)

if __name__ == "__main__":
    MainClass()
