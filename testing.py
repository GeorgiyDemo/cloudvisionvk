from PIL import ImageFont, ImageDraw, Image
"""
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
"""
def get_resolution(box):
    buf_list = []
    for i in range(-1,len(box)-1):
        x,y = box[i]
        x1, y1 = box[i+1]
        buf_list.append((x-x1,y-y1))
    
    out_h, out_w = 0, 0
    for h, w in buf_list:
        if h != 0.0:
            out_h = abs(h)
        if w != 0.0:
            out_w = abs(w)
    
    return out_h, out_w


        

       


box = [(431.35243463516235, 383.94355031847954), (671.1889901161194, 383.94355031847954), (671.1889901161194, 712.4056348800659), (431.35243463516235, 712.4056348800659)]
result = get_resolution(box)
print(result)