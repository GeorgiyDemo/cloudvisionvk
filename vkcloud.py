import pymysql.cursors, vk, time, json, uuid, random, io, re, os, time, requests
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision

USER_TOKEN = "USER_TOKEN"
CLUB_TOKEN = "CLUB_TOKEN"
TTF_DIR = "~/Library/Fonts/MuseoSansCyrl-300.ttf"
CLUB_ID = "-175867271"

def getfile(url):
	thisfilename = str(uuid.uuid4())+".jpg"
	r = requests.get(url, stream=True)
	with open(thisfilename, 'wb') as fd:
		for chunk in r.iter_content(2000):
			fd.write(chunk)
	return thisfilename

def localize_objects(path):

    obj_of_objects = {}
    allcoords = []
           
    im = Image.open(path)
    draw = ImageDraw.Draw(im)
    client = vision.ImageAnnotatorClient()
    with open(path, 'rb') as image_file:
        content = image_file.read()
        image = vision.types.Image(content=content)

    objects = client.object_localization(image=image).localized_object_annotations

    for object_ in objects:

        obj_of_objects[object_.name]=object_.score
        box = [(vertex.x*im.width, vertex.y*im.height) for vertex in object_.bounding_poly.normalized_vertices]
                
        if box not in allcoords:
            allcoords.append(box)
            r = lambda: random.randint(0,255)
            draw.line(box + [box[0]], width=5, fill='#%02X%02X%02X' % (r(),r(),r()))
            draw.text(box[0], object_.name+" "+str(object_.score), font=ImageFont.truetype(TTF_DIR, 30))
    image_file.close()
    im.save(path)
    return obj_of_objects

def objects_formater(obj):
	out_str = "" 
	for key in obj:
		out_str += key+" "+str(int(round(obj[key],2)*100))+"%\n"
	return out_str

def main():

	main_obj = {}
	#Основная конфигурация
	VKSession = vk.Session(access_token=CLUB_TOKEN)

	request_keyboard = {
	"one_time":True,
	"buttons":[
		[
			{
			"action":{
				"type":"text",
				"payload":"{\"button\": \"1\"}",
				"label":"Да"
			},
			"color":"primary"
			},

			{
			"action":{
				"type":"text",
				"payload":"{\"button\": \"2\"}",
				"label":"Нет"
			},
			"color":"negative"
			},

		]
	]
	}

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
		if 'failed' in response:
			key = api.messages.getLongPollServer(v=APIVersion)['key']
		else:
			for i in range(len(response['updates'])):
				if checker != True:
					try:
							
						message_longpoll = response['updates'][i][5]
						chat_longpoll = response['updates'][i][3]
						attaches = response['updates'][0][6]
						checker = True

					except:
						pass

			if checker == False:
				attaches = [0]
				message_longpoll = [0]
				chat_longpoll = [0]

			ts = response['ts']


			#Чекаем входящие сообщения
			if message_longpoll != [0]:

				if message_longpoll == "Да":
					if chat_longpoll in main_obj:
						api.messages.send(user_id=chat_longpoll,message="Готово ✨",v=APIVersion)

						UserVKSession = vk.Session(access_token=USER_TOKEN)
						UserAPI = vk.API(UserVKSession)
						user_server_url = UserAPI.photos.getWallUploadServer(group_id=CLUB_ID[1:],v=APIVersion)["upload_url"]

						user_photo_response = requests.post(user_server_url,files={'photo': open(main_obj[chat_longpoll][0], 'rb')}).json()
						user_photo_final = UserAPI.photos.saveWallPhoto(group_id=CLUB_ID[1:],photo=user_photo_response["photo"],server=user_photo_response["server"],hash=user_photo_response["hash"],caption=main_obj[chat_longpoll][1],v=APIVersion)[0]
						user_photo_str = "photo"+str(user_photo_final["owner_id"])+"_"+str(user_photo_final["id"])
						
						UserAPI.wall.post(owner_id=CLUB_ID,from_group=1,message=main_obj[chat_longpoll][1],attachments=user_photo_str,v=APIVersion)
						os.remove(main_obj[chat_longpoll][0])
						main_obj.pop(chat_longpoll, None)

				elif message_longpoll == "Нет":
					if chat_longpoll in main_obj:
						api.messages.send(user_id=chat_longpoll,message="Хорошо 😌",v=APIVersion)
						os.remove(main_obj[chat_longpoll][0])
						main_obj.pop(chat_longpoll, None)

				elif "attach1_type" in attaches:
					if attaches["attach1_type"] == "photo":
						photo_json = api.messages.getById(message_ids=response['updates'][0][1],v=APIVersion)["items"][0]["attachments"][0]["photo"]
								
						#Простите
						keyname = ""
						for key in photo_json:
							if key[:5] == "photo":
								keyname = key

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

if __name__ == '__main__':
	main()