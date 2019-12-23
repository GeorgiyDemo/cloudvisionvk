import time, json, uuid, random, io, re, os, time, requests
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision

TTF_DIR = "./MuseoSansCyrl-300.ttf"

class PhotoProcessing():

    def __init__(self, path):
        self.path = path
        self.results = None
        self.image = None
        self.localize_objects()

    def string_formater(self):
        all_objects = self.results
        out_str = "" 
        for key in all_objects:
            out_str += key+" "+str(int(round(all_objects[key],2)*100))+"%\n"
        self.results = out_str

    def localize_objects(self):

        path = self.path

        obj_of_objects = {}
        allcoords = []

        #Открытие изображения    
        im = Image.open(path)
        draw = ImageDraw.Draw(im)
        
        client = vision.ImageAnnotatorClient()
        
        with open(path, 'rb') as image_file:
            content = image_file.read()
            image = vision.types.Image(content=content)

        #Все объекты
        objects = client.object_localization(image=image).localized_object_annotations

        #Цикл по каждому объекту
        for obj in objects:

            obj_of_objects[obj.name]=obj.score
            box = [(vertex.x*im.width, vertex.y*im.height) for vertex in obj.bounding_poly.normalized_vertices]
                    
            if box not in allcoords:
                allcoords.append(box)
                r = lambda: random.randint(0,255)
                draw.line(box + [box[0]], width=5, fill='#%02X%02X%02X' % (r(),r(),r()))
                draw.text(box[0], obj.name+" "+str(obj.score), font=ImageFont.truetype(TTF_DIR, 30))
        
        self.image = im
        self.results = obj_of_objects

if __name__ == "__main__":

    thisfilename = "15763474458860.png"
    detector = PhotoProcessing(thisfilename)
    detector.image.save(thisfilename)
    print(detector.results)