from PIL import Image, ImageDraw, ImageFont

# ImageDraw.text(xy, text, fill=None, font=None, anchor=None, spacing=4, align='left', 
# direction=None, features=None, language=None, stroke_width=0, stroke_fill=None, embedded_color=False)

# create an image
out = Image.new("RGB", (150, 100), (255, 255, 255))

# get a font
fnt = ImageFont.truetype("modules/Roboto-Regular.ttf", size= 40)
# get a drawing context
d = ImageDraw.Draw(out) #PIL.ImageDraw.Draw(im, mode=None

# draw multiline text
d.text((10,10), "reee\nreee", font=fnt, fill=(0, 0, 0))

out.show()