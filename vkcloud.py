import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import imageprocessing

#def write_msg(user_id, message):
#    vk.method('messages.send', {'user_id': user_id, 'random_id': get_random_id(), 'message': message})


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
        #Находим все размеры фоточки
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
                        obj = imageprocessing.PhotoProcessing(url)


                        #url = attachments["attach1"]
                        # Сообщение от пользователя

                        """
                        server_url = api.photos.getMessagesUploadServer(peer_id=chat_longpoll,v=APIVersion)["upload_url"]
                            thisfilename = getfile(photo_json[keyname])
                            message_final = objects_formater(localize_objects(thisfilename))
                                photo_response = requests.post(server_url,files={'photo': open(thisfilename, 'rb')}).json()
                                photo_final = api.photos.saveMessagesPhoto(photo=photo_response["photo"],server=photo_response["server"],hash=photo_response["hash"],v=APIVersion)[0]
                                photo_str = "photo"+str(photo_final["owner_id"])+"_"+str(photo_final["id"])
                                if message_final == "":
                                    api.messages.send(user_id=chat_longpoll,message="Нет результатов для этого фото\nПопробуй другое 👀",v=APIVersion)
                                else:
                                    api.messages.send(user_id=chat_longpoll,message="Ваши результаты:\n"+message_final+"\nХотите поделиться этим фото в сообществе?",attachment=photo_str,keyboard=json.dumps(request_keyboard,ensure_ascii=False),v=APIVersion)
                                    main_obj[chat_longpoll]=[thisfilename, message_final]
                        """

if __name__ == "__main__":
    MainClass()