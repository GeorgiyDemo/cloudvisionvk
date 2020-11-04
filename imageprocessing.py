import uuid
from random import randint

import requests
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision


class PhotoProcessing:
    def __init__(self, url, ttf_dir, modes_list):
        self.modes_list = modes_list
        self.url = url
        self.ttf_dir = ttf_dir
        self.path = None
        self.results = None
        self.image = None
        self.get_file()

        if "adaptive_font" in modes_list:
            self.localize_objects_adaptive()
        else:
            self.localize_objects()

    def get_file(self):
        """
        Метод для получения отправленного пользователем фото с vk
        """
        url = self.url
        path = str(uuid.uuid4()) + ".jpg"
        r = requests.get(url, stream=True)

        with open(path, "wb") as fd:
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
        with open(path, "rb") as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
        # Получаем все объекты
        objects = client.object_localization(image=image).localized_object_annotations

        # Цикл по каждому объекту
        for obj in objects:

            # Добавляем объект в словарь
            obj_of_objects[obj.name] = obj.score

            # Определение контура-прямоугольника с координатами
            box = [
                (vertex.x * im.width, vertex.y * im.height)
                for vertex in obj.bounding_poly.normalized_vertices
            ]
            # Если это новый контур, то он не в all_coords
            if box not in all_coords:

                all_coords.append(box)
                # Рандомный цвет обводки
                r = lambda: randint(0, 255)
                # Рисуем линию + текст
                draw.line(
                    box + [box[0]], width=5, fill="#%02X%02X%02X" % (r(), r(), r())
                )
                if "black_text" in self.modes_list:
                    draw.text(
                        box[0],
                        obj.name + " " + str(obj.score),
                        font=ImageFont.truetype(self.ttf_dir, 30),
                        fill=(0, 0, 0),
                    )
                else:
                    draw.text(
                        box[0],
                        obj.name + " " + str(obj.score),
                        font=ImageFont.truetype(self.ttf_dir, 30),
                        fill=(255, 255, 255),
                    )

        im.save(path)
        self.results = obj_of_objects

    def get_resolution(self, box):
        """
        Странный метод определения разрешения изображения из boundingbox
        Необходим для логики localize_objects_adaptive
        """
        buf_list = []
        for i in range(-1, len(box) - 1):
            x, y = box[i]
            x1, y1 = box[i + 1]
            buf_list.append((x - x1, y - y1))

        out_w = 0
        for w, _ in buf_list:
            if w != 0.0:
                out_w = abs(w)

        return out_w

    def localize_objects_adaptive(self):
        """
        Метод для формирования, отправки и получения запроса с Google Cloud
        Использует адаптивный шрифт
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
        with open(path, "rb") as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
        # Получаем все объекты
        objects = client.object_localization(image=image).localized_object_annotations

        # Цикл по каждому объекту
        for obj in objects:

            # Добавляем объект в словарь
            obj_of_objects[obj.name] = obj.score

            # Определение контура-прямоугольника с координатами
            box = [
                (vertex.x * im.width, vertex.y * im.height)
                for vertex in obj.bounding_poly.normalized_vertices
            ]

            # Если это новый контур, то он не в all_coords
            if box not in all_coords:

                all_coords.append(box)

                txt = obj.name + " " + str(int(round(obj.score, 2) * 100)) + "%"
                # Изначально шрифт 1
                fontsize = 1

                # Получаем разрешение изображения
                width = self.get_resolution(box)
                # 60% boundingbox используется
                img_fraction = 0.6

                font = ImageFont.truetype(self.ttf_dir, fontsize)
                # Пока шрифт будет влезать в диапазон
                while font.getsize(txt)[0] < img_fraction * width:
                    fontsize += 1
                    font = ImageFont.truetype(self.ttf_dir, fontsize)
                fontsize -= 1

                r = lambda: randint(0, 255)
                draw.line(
                    box + [box[0]], width=5, fill="#%02X%02X%02X" % (r(), r(), r())
                )
                if "black_text" in self.modes_list:
                    draw.text(
                        box[0],
                        txt,
                        font=ImageFont.truetype(self.ttf_dir, fontsize),
                        fill=(0, 0, 0),
                    )
                else:
                    draw.text(
                        box[0],
                        txt,
                        font=ImageFont.truetype(self.ttf_dir, fontsize),
                        fill=(255, 255, 255),
                    )

        im.save(path)
        self.results = obj_of_objects
