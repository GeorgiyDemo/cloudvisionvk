import uuid
from random import randint

import requests
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision
from vk_api.utils import get_random_id

TTF_DIR = "./MuseoSansCyrl-300.ttf"


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

        server_url = self.vk.method('photos.getMessagesUploadServer', {'peer_id': self.user_id})["upload_url"]
        photo_r = requests.post(server_url, files={'photo': open(self.path, 'rb')}).json()
        photo_final = self.vk.method("photos.saveMessagesPhoto",
                                     {"photo": photo_r["photo"], "server": photo_r["server"], "hash": photo_r["hash"]})[
            0]
        photo_str = "photo" + str(photo_final["owner_id"]) + "_" + str(photo_final["id"])
        self.photo_str = photo_str

    def message_sender(self):
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


class PhotoProcessing():

    def __init__(self, url):
        self.url = url
        self.path = None
        self.results = None
        self.image = None
        self.get_file()
        self.localize_objects()

    def get_file(self):
        """
        Метод для получения отправленного пользователем фото с vk
        """
        url = self.url
        path = str(uuid.uuid4()) + ".jpg"
        r = requests.get(url, stream=True)

        with open(path, 'wb') as fd:
            for chunk in r.iter_content(2000):
                fd.write(chunk)

        self.path = path

    def string_formater(self):
        """
        Метод для отдачи форматированной строки
        """
        all_objects = self.results
        out_str = ""
        for key in all_objects:
            out_str += key + " " + str(int(round(all_objects[key], 2) * 100)) + "%\n"
        self.results = out_str

    def localize_objects(self):
        """
        Метод для формирования, отправки и получения запроса с Google Cloud
        """

        path = self.path

        # Словарь со всеми объектами
        obj_of_objects = {}
        # Список для временного хранения координат boundingbox
        all_coords = []

        # Открытие изображения
        im = Image.open(path)
        draw = ImageDraw.Draw(im)

        # Клиент
        client = vision.ImageAnnotatorClient()
        with open(path, 'rb') as image_file:
            content = image_file.read()
            image = vision.types.Image(content=content)
        # Получаем все объекты
        objects = client.object_localization(image=image).localized_object_annotations

        # Цикл по каждому объекту
        for obj in objects:

            # Добавляем объект в словарь
            obj_of_objects[obj.name] = obj.score

            # Определение контура-прямоугольника с координатами
            box = [(vertex.x * im.width, vertex.y * im.height) for vertex in obj.bounding_poly.normalized_vertices]

            # Если это новый контур, то он не в all_coords
            if box not in all_coords:
                all_coords.append(box)
                # Рандомный цвет обводки
                r = lambda: randint(0, 255)
                # Рисуем линию + текст
                draw.line(box + [box[0]], width=5, fill='#%02X%02X%02X' % (r(), r(), r()))
                draw.text(box[0], obj.name + " " + str(obj.score), font=ImageFont.truetype(TTF_DIR, 30), fill=(0,0,0,0))
                #draw.text(box[0], obj.name + " " + str(obj.score), font=ImageFont.truetype(TTF_DIR, 30))

        im.save(path)
        self.results = obj_of_objects


def async_processing(vk, user_id, url):
    detector = PhotoProcessing(url)
    VkProcessing(vk, user_id, detector.path, detector.results)
