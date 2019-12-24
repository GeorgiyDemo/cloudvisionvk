import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import multiprocessing as mp
import imageprocessing

class MainClass():
    def __init__(self):
        # API-ключ созданный ранее
        token = ""
        # Авторизуемся как сообщество
        self.vk = vk_api.VkApi(token=token)
        self.processing()

    def get_url(self, message_id):
        """
        Метод для получения url изобржения из id сообщения
        """
        #Получаем сообщеньку по методу
        r = self.vk.method('messages.getById', {'message_ids': message_id})["items"]
        #Находим все размеры фото
        all_sizes = r[0]["attachments"][0]["photo"]["sizes"]

        #В цикле по каждой ищем самое большое изображение
        height, width, index = 0, 0, 0
        for i in range(len(all_sizes)):
            if all_sizes[i]["width"] > width and all_sizes[i]["height"] > height:
                height = all_sizes[i]["height"]
                width = all_sizes[i]["width"]
                index = i
        
        #Обращаемся к полученному индексу
        url = all_sizes[index]["url"]

        #Берем последний элемент списка (т.к. он самый большой)
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
                    msg_id = event.message_id
                    
                    attachments = event.attachments
                    if attachments != {} and attachments["attach1_type"] == "photo":
                        url = self.get_url(msg_id)

                        p = mp.Process(target=imageprocessing.async_processing, args=(self.vk, event.user_id, url,))
                        p.start()
                        

                        #url = attachments["attach1"]
                        # Сообщение от пользователя

if __name__ == "__main__":
    MainClass()