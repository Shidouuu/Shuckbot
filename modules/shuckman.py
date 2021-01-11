import random, discord
from requests import get as reGet
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


inp_shell = reGet("https://i.imgur.com/bbhRsZ4.png")
inp_limb1 = reGet("https://i.imgur.com/MwaEp9Y.png")
inp_limb2 = reGet("https://i.imgur.com/WwbPhmL.png")
inp_limb3 = reGet("https://i.imgur.com/U9pBmxL.png")
inp_limb4 = reGet("https://i.imgur.com/Wa4uDJH.png")
inp_shuckPole = reGet("https://i.imgur.com/OfPaN9Z.png")
inp_shuckNoose = reGet("https://i.imgur.com/QNisicJ.png")
inp_shuckDead  = reGet("https://i.imgur.com/vsQ4fM6.png")

open_shell = Image.open(BytesIO(inp_shell.content))
open_limb1 = Image.open(BytesIO(inp_limb1.content))
open_limb2 = Image.open(BytesIO(inp_limb2.content))
open_limb3 = Image.open(BytesIO(inp_limb3.content))
open_limb4 = Image.open(BytesIO(inp_limb4.content))
open_shuckPole = Image.open(BytesIO(inp_shuckPole.content))
open_shuckNoose = Image.open(BytesIO(inp_shuckNoose.content))
open_shuckDead = Image.open(BytesIO(inp_shuckDead.content))


with open(r'C:\users\guitar god\documents\python\shuckbot\shuckbot-testing\modules\words_alpha.txt') as words_file:
    word_list = words_file.read().splitlines()


class img():
    '''Used for drawing text on images relating to the ShuckMan game'''

    def __init__(self, txt, inp_img, fnt):
        self.text = txt
        self.inp_img = inp_img
        self.fnt = ImageFont.truetype("modules/Roboto-Regular.ttf", size= fnt)

    # ImageDraw.text(xy, text, fill=None, font=None, anchor=None, spacing=4, align='left', 
    # direction=None, features=None, language=None, stroke_width=0, stroke_fill=None, embedded_color=False)
    async def tLeft(self):
        image = ImageDraw.Draw(self.inp_img)
        image.text((10,10), self.txt, font=fnt, fill=(0, 0, 0))
        self.open_shell.save("tLeft.png")
    
    async def main_text(self):
        print(self.txt)
        x, y = self.inp_img.size 
        pos = x/2
        image = ImageDraw.Draw(self.inp_img)
        image.text((20,20), self.txt, font=fnt, fill=(255, 255, 255))

        self.open_shell.save("mainText.png")


by_length = {}
for word in word_list:
    by_length.setdefault(len(word), []).append(word)

async def word_finder(wordlength):
    '''Finds the length of the word from words_alpha'''
    global word
    word = random.choice(by_length[wordlength])
    print(word)
  
    
async def shuckMan(message):

    content = message.clean_content[11:]
    print(content)

    if content.lower() == "5":
        z = img()
        w = img()

        embed = discord.Embed(title="ShuckMan™                                  Easy Difficulty") 
        embed.type = "rich"
        embed.colour = discord.Color.gold() 

        await word_finder(5) #Calls the word_finder function and tells it the word length (5) desired
        await z.tLeft(txt="Game start!", inp_img= z.open_shell) #Tells the tLeft method to write "Game start!" in the upper left corner of the image
        await w.main_text(txt=word, inp_img=Image.open("tLeft.png")) #Opens the saved tLeft.png image and writes the word on top of it
        
        embed.set_image(url="attachment://mainText.png") #Designates the final image into an embed
        await message.channel.send(embed=embed, file=discord.File("mainText.png")) #Sends the message
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       # await message.channel.send(random.choice(words[1]))





   # with open('words_alpha.txt') as words_file:
   #     words = words_file.read().splitlines()

   # print(random.choice(words))