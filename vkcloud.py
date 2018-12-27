import pymysql.cursors, vk, time, json, requests, uuid
import argparse, random, io, re, os, time, requests
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision

VK_TOKEN = "VK_TOKEN"

def getfile(url):
	thisfilename = str(uuid.uuid4())
	r = requests.get(url, stream=True)
	with open(thisfilename, 'wb') as fd:
		for chunk in r.iter_content(2000):
			fd.write(chunk)
	return thisfilename

def localize_objects(path):
    coords = []
    allcoords = []
           
    im = Image.open(path)
    draw = ImageDraw.Draw(im)
    client = vision.ImageAnnotatorClient()
    with open(path, 'rb') as image_file:
        content = image_file.read()
        image = vision.types.Image(content=content)

    objects = client.object_localization(image=image).localized_object_annotations

    for object_ in objects:
                    
        box = [(vertex.x*im.width, vertex.y*im.height) for vertex in object_.bounding_poly.normalized_vertices]
                
        if box not in allcoords:
            allcoords.append(box)
            r = lambda: random.randint(0,255)
            draw.line(box + [box[0]], width=5, fill='#%02X%02X%02X' % (r(),r(),r()))
            draw.text(box[0], object_.name+" "+str(object_.score), font=ImageFont.truetype("~/Library/Fonts/MuseoSansCyrl-300.ttf",30))
    image_file.close()
    im.save("output"+path+".png")

def main():
	#Основная конфигурация
	VKSession = vk.Session(access_token=VK_TOKEN)

	api = vk.API(VKSession)
	APIVersion = 5.73
	message_longpoll = [0]

	#Настройка лонгпула
	server = None
	key    = None
	ts     = None


	while True:

		#Фикс лонпула по харду
		if server == None:
			cfg = api.messages.getLongPollServer(v=APIVersion)
			server = cfg['server']
			key = cfg['key']
			ts = cfg['ts']

		response = requests.post(
			"https://{server}?act=a_check&key={key}&ts={ts}&wait=25&mode={mode}&version=2".format(**{
				"server": server,
				"key": key,
				"ts": ts,
				"mode": 2
			}),
		timeout=30
		).json()

		checker = False
		try:
			for i in range(len(response['updates'])):
				if checker != True:
					try:
						
						message_longpoll = response['updates'][i][5]
						chat_longpoll = response['updates'][i][3]
						checker = True

					except:
						pass

			if checker == False:
				message_longpoll = [0]
				chat_longpoll = [0]

			ts = response['ts']


			#Чекаем входящие сообщения
			if message_longpoll != [0]:
				attaches = response['updates'][0][6]
				if attaches["attach1_type"] == "photo":
					photo_json = api.messages.getById(message_ids=response['updates'][0][1],v=APIVersion)["items"][0]["attachments"][0]["photo"]
						
					#Простите
					keyname = ""
					for key in photo_json:
						if key[:5] == "photo":
							keyname = key
					localize_objects(getfile(photo_json[keyname]))
		
		except KeyError:
			pass

if __name__ == '__main__':
	main()