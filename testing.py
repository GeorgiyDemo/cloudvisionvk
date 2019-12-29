from PIL import ImageFont, ImageDraw, Image

ttf_dir = "./MuseoSansCyrl-300.ttf"
image = Image.open('1.png')
draw = ImageDraw.Draw(image)
txt = "Hello World"
fontsize = 1  # starting font size

# portion of image width you want text width to be
img_fraction = 0.50

font = ImageFont.truetype(ttf_dir, fontsize)
while font.getsize(txt)[0] < img_fraction*image.size[0]:
    # iterate until the text size is just larger than the criteria
    fontsize += 1
    font = ImageFont.truetype(ttf_dir, fontsize)

# optionally de-increment to be sure it is less than criteria
fontsize -= 1
font = ImageFont.truetype(ttf_dir, fontsize)

print('final font size',fontsize)
draw.text((10, 25), txt, font=font) # put the text on the image
image.save('hsvwheel_txt.png') # save it