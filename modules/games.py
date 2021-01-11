import discord
from PIL import Image, ImageChops, ImageColor
import numpy as np
import random
import time
from colormath.color_objects import XYZColor, sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cmc
import asyncio
from requests import get #Remind me if I forgot to include this change in the commit or whatever
from io import BytesIO
from . import flags

async def game(message, client):
    try:
        args = [x.lower() for x in message.clean_content[1:].split(' ')][1:]
    except IndexError:
        await message.channel.send("**The list of available games are:**\n\t*;game colour* - guess the hexcode!")
        return
    if args[0] in ("color", "col", "c"):
        if len(args) > 2 and args[1] in ("m", "mp", "multi", "multiplayer") and args[2].isdigit():
            await colour_guesser_multi(message, client, game_time=int(args[2]))
        elif len(args) > 1 and args[1] in ("m", "mp", "multi", "multiplayer"):
            await colour_guesser_multi(message, client)
        else:
            await colour_guesser(message, client)
    elif args[0] in ("colour"):
        if len(args) > 1 and args[1] in ("m", "mp", "multi", "multiplayer"):
            await colour_guesser_multi(message, client, "u")
        else:
            await colour_guesser(message, client, "u")
    elif args[0] in ("flag", "flags", "f"):
        if len(args) == 1:
            await flag_guesser(message, client)
        elif args[1] in ("easy", "e", "1"):
            await flag_guesser(message, client, 1)
        elif args[1] in ("normal", "n", "2"):
            await flag_guesser(message, client, 2)
        elif args[1] in ("hard", "h", "3"):
            await flag_guesser(message, client, 3)
        elif args[1] in ("states", "s", "4"):
            await flag_guesser(message, client, 4)
        elif args[1] in ("expert", "extreme", "x", "5"):
            await flag_guesser(message, client, 5)
        elif args[1] in ("master", "all", "m", "a", "6"):
            await flag_guesser(message, client, 6)
        else:
            await flag_guesser(message, client)


async def colour_guesser(message, client, _letter=""):
    size = 150
    mention = message.author.mention
    col = hex(random.getrandbits(24))[2:]
    while len(col) < 6:
        col = '0' + col
        print(col)

    try:
        img = Image.new("RGB", (size, size), ImageColor.getcolor(('#' + col), "RGB"))
    except ValueError:
        await message.channel.send("Value Error has been thrown!")
    else:
        img.save("colourguess.png")
        await message.channel.send(mention + ", here is your colo" + _letter + "r! Try to guess its hex code!",
                                   file=discord.File("colourguess.png"))

    def check(m):
        return m.author == message.author and m.channel == message.channel

    t = time.time()
    msg = await client.wait_for('message', check=check)
    new_time = time.time()
    msg_content = msg.content

    if msg_content[0] == '#':
        msg_content = msg_content[1:]

    def is_hex(s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

    if len(msg_content) != 6 or not is_hex(msg_content):
        await message.channel.send(
            "Sorry, your answer was not formatted correctly! Your answer should just be the 6 digit "
            "hexadecimal code for your guess, and nothing else! The actual colo" + _letter + "r was "
            + col + " !")
        return

    r = int(msg_content[0:2], 16)
    g = int(msg_content[2:4], 16)
    b = int(msg_content[4:6], 16)

    ar = int(col[0:2], 16)
    ag = int(col[2:4], 16)
    ab = int(col[4:6], 16)

    score = calculate_score(r, g, b, ar, ag, ab)
    letter = "s"
    if score == 1:
        letter = ''

    img.paste(Image.new("RGB", (size // 2, size), ImageColor.getcolor(('#' + msg_content), "RGB")),
              (size // 2, 0))
    img.save("clrguessresult.png")

    await message.channel.send("The actual colo" + _letter + "r was " + col + "!\n" + mention + " got " +
                               str(int(score)) + "/100 point" + letter + "\n"
                                                                         "You took %.1f seconds to guess!"
                               % (new_time - t), file=discord.File("clrguessresult.png"))


async def colour_guesser_multi(message, client, _letter="", game_time=15):
    if game_time > 60:
        game_time = 60
    size = 150
    col = hex(random.getrandbits(24))[2:]
    while len(col) < 6:
        col = '0' + col
        print(col)
    msg = None
    try:
        img = Image.new("RGB", (size, size), ImageColor.getcolor(('#' + col), "RGB"))
    except ValueError:
        await message.channel.send("Value Error has been thrown!")
    else:
        img.save("colourguess.png")
        msg = await message.channel.send("Here is your colo" + _letter + "r! Everyone try to guess its hex code!"
                                                                         "\nYou have " + str(game_time) + " seconds...",
                                         file=discord.File("colourguess.png"))

    def is_valid_hex(s):
        try:
            int(s, 16)
            return len(s) == 6
        except ValueError:
            return False

    await asyncio.sleep(game_time)
    msgs = message.channel.history(limit=50)
    guess_msgs = []
    users = []
    final_guesses = []
    winner = [0, "", -1]
    async for x in msgs:
        if x.id == msg.id:
            break
        if is_valid_hex(x.clean_content):
            guess_msgs.append(x)

    for x in guess_msgs:
        if x.author.id in users:
            continue
        final_guesses.append([x.author.id, x.clean_content])
        users.append(x.author.id)

    ar = int(col[0:2], 16)
    ag = int(col[2:4], 16)
    ab = int(col[4:6], 16)

    for x in range(0, len(final_guesses)):
        rs = final_guesses[x][1][0:2]
        gs = final_guesses[x][1][2:4]
        bs = final_guesses[x][1][4:6]
        r = int(rs, 16)
        g = int(gs, 16)
        b = int(bs, 16)
        score = calculate_score(r, g, b, ar, ag, ab)
        final_guesses[x] = [final_guesses[x][0], final_guesses[x][1], score]
        if score > winner[2]:
            winner = final_guesses[x]

    if not final_guesses:
        await message.channel.send("Time out! Nobody guessed!")
    else:
        final_guesses.sort(key=lambda y: y[2], reverse=True)
        guesses = len(final_guesses)
        for x in range(0, guesses):
            img.paste(Image.new("RGB", (size // 2, size), ImageColor.getcolor(('#' + final_guesses[x][1]), "RGB")),
                      (size // 2, x * size // guesses))
        img.save("clrguessresult.png")
        await message.channel.send(
            "The actual colo" + _letter + "r was " + col + "!\n" + client.get_user(int(winner[0])).mention
            + " got " + str(int(np.ceil(winner[2]))) + "/100 points\n"
            , file=discord.File("clrguessresult.png"))
        to_send = ""
        for x in range(0, len(final_guesses)):
            to_send += str(x + 1) + ". " + client.get_user(final_guesses[x][0]).mention + ": " + \
                       str(int(np.ceil(final_guesses[x][2]))) + "/100 points (#" + final_guesses[x][1] + ")\n"
        await message.channel.send(to_send)


def rgb_to_lab(r, g, b):
    cr = r / 255
    cg = g / 255
    cb = b / 255

    rgb_obj = sRGBColor(cr, cg, cb)
    xyz_obj = convert_color(rgb_obj, XYZColor)
    return convert_color(xyz_obj, LabColor)


def calculate_score(r, g, b, ar, ag, ab):
    lab_obj = rgb_to_lab(r, g, b)
    a_lab_obj = rgb_to_lab(ar, ag, ab)

    difference = delta_e_cmc(lab_obj, a_lab_obj)
    res = (100 - (difference - 2) ** 0.7 * (23 / 3)) if difference > 2 else 100
    return res if res > 0 else 0

async def flag_guesser(message, client, difficulty=0):
    lengths = [0, 0, 0, 0, 0]
    typeF = ["country", "country", "country", "country", "state", "flag", "flag"]
    for c in flags.flaglist.flags:
        lengths[c["difficulty"]-1] += 1
    # print(lengths)
    min_index = 0
    game_time = 15

    if difficulty == 1:
        max_index = lengths[0]
    elif difficulty == 2:
        min_index = lengths[0] + 1
        max_index = lengths[0] + lengths[1]
    elif difficulty == 3:
        min_index = lengths[0] + lengths[1] + 1
        max_index = lengths[0] + lengths[1] + lengths[2]
    elif difficulty == 4:
        min_index = lengths[0] + lengths[1] + lengths[2] + 1
        max_index = lengths[0] + lengths[1] + lengths[2] + lengths[3]
    elif difficulty == 5:
        min_index = lengths[0] + lengths[1] + lengths[2] + 1
        max_index = lengths[0] + lengths[1] + lengths[2] + lengths[3] + lengths[4]
    elif difficulty == 6:
        max_index = len(flags.flaglist.flags)
    else:
        max_index = lengths[0] + lengths[1] + lengths[2]

    country_index = random.randint(min_index, max_index)

    # try:
    #     if flags[country_index]["name"] == "Israel" and message.channel.guild == 522565286168363009:
    #         country_index = 0
    # except IndexError:
    #     country_index = 0
    # country_index = 30

    try:
        response = get(flags.flaglist.flags[country_index]["url"])
        flag_img = Image.open(BytesIO(response.content))
        flag_img.save("flag.png")
    except:
        print(flags[country_index]["url"])
        return

    embed = discord.Embed(title="You have " + str(game_time) + " seconds to guess the " + typeF[difficulty] + "!")
    embed.colour = discord.Color.gold()
    embed.type = "rich"

    embed.set_image(url="attachment://flag.png")
    try:
        await message.channel.send(embed=embed, file=discord.File("flag.png"))
    except:
        print(flags.flaglist.flags[country_index]["url"])
        return
    # await message.channel.send("You have " + str(game_time) + " seconds to guess the flag!", file=discord.File("flag.png"))

    def check(m):
        if type(flags.flaglistflags[country_index]["name"]) is tuple:
            for n in flags.flaglistflags[country_index]["name"]:
                if n.lower() == m.content.lower() and m.channel == message.channel:
                    return True
            return False
        return m.channel == message.channel and (m.content.lower() == flags[country_index]["name"].lower())

    t = time.time()
    try:
        msg = await client.wait_for('message', check=check, timeout=game_time)
    except:
        try:
            await message.channel.send("Sorry, nobody got the " + typeF[difficulty] + " correct! The correct answer was: " + flags.flaglist.flags[country_index]["name"])
        except TypeError:
            await message.channel.send("Sorry, nobody got the " + typeF[difficulty] + " correct! The correct answer was: " + flags.flaglist.flags[country_index]["name"][0])
        return
    try:
        await message.channel.send("Good job " + msg.author.mention + "! The " + typeF[difficulty] + " was " + flags[country_index]['name'])
    except TypeError:
        await message.channel.send("Good job " + msg.author.mention + "! The " + typeF[difficulty] + " was " + flags[country_index]['name'][0])









# difference = abs(actual_r - r) + abs(actual_g - g) + abs(actual_b - b)

# a = 0.39
# f = 1.05
# g = 0.14
# h = 26
# x = difference
# # score = max((-100*np.e**(a*(difference+b)))/(np.e**a*(difference+b) + 100) + 102.85 - c*np.sqrt(difference), 0)
# score = np.ceil(max(((-100 * np.e**(a*x))/(np.e**(a*x)+120)+100.75),
# 					(((-100 * np.e**(g*(x+h)))/(np.e**(g*(x+h))+120) + 100)/f)))
# score = 0 if x > 60 else score

# scale = 0.045
# score = np.ceil((-100 * np.e ** (scale * difference)) / (np.e ** (scale * difference) + 120) + 100)
# res = (100 - (difference - 2)**0.8 * (11 / 3)) if difference > 2 else 100
# res = (100 - difference * (1 + 2/3)) if difference > 2 else 100
# if difference > 400:
# 	score = 0




# easy_flags = [
# {"name": ("Australia"), "difficulty": 1, "url": ""},
# {"name": ("Austria"), "difficulty": 1, "url": ""},
# {"name": ("Belgium"), "difficulty": 1, "url": ""},
# {"name": ("Brazil"), "difficulty": 1, "url": ""},
# {"name": ("Canada"), "difficulty": 1, "url": ""},
# {"name": ("China"), "difficulty": 1, "url": ""},
# {"name": ("Denmark"), "difficulty": 1, "url": ""},
# {"name": ("Finland"), "difficulty": 1, "url": ""},
# {"name": ("France"), "difficulty": 1, "url": ""},
# {"name": ("Germany"), "difficulty": 1, "url": ""},
# {"name": ("Iceland"), "difficulty": 1, "url": ""},
# {"name": ("India"), "difficulty": 1, "url": ""},
# {"name": ("Indonesia"), "difficulty": 1, "url": ""},
# {"name": ("Republic of Ireland","Ireland"), "difficulty": 1, "url": ""},
# {"name": ("Israel"), "difficulty": 1, "url": ""},
# {"name": ("Italy"), "difficulty": 1, "url": ""},
# {"name": ("Japan"), "difficulty": 1, "url": ""},
# {"name": ("Mexico"), "difficulty": 1, "url": ""},
# {"name": ("Kingdom of the Netherlands","Netherlands"), "difficulty": 1, "url": ""},
# {"name": ("New Zealand"), "difficulty": 1, "url": ""},
# {"name": ("Norway"), "difficulty": 1, "url": ""},
# {"name": ("Poland"), "difficulty": 1, "url": ""},
# {"name": ("Portugal"), "difficulty": 1, "url": ""},
# {"name": ("South Korea","Republic of Korea"), "difficulty": 1, "url": ""},
# {"name": ("Russia","Russian Federation"), "difficulty": 1, "url": ""},
# {"name": ("South Africa"), "difficulty": 1, "url": ""},
# {"name": ("Spain"), "difficulty": 1, "url": ""},
# {"name": ("Sweden"), "difficulty": 1, "url": ""},
# {"name": ("Switzerland"), "difficulty": 1, "url": ""},
# {"name": ("Turkey"), "difficulty": 1, "url": ""},
# {"name": ("Ukraine"), "difficulty": 1, "url": ""},
# {"name": ("United Kingdom","United Kingdom of Great Britain and Northern Ireland","The UK","UK"), "difficulty": 1, "url": ""},
# {"name": ("The United States","United States","United States of America","the United States of America","the US","USA","the USA","US"), "difficulty": 1, "url": ""}
# ]
#
# normal_flags = [
# {"name": ("Albania"), "difficulty": 2, "url": ""},
# {"name": ("Algeria"), "difficulty": 2, "url": ""},
# {"name": ("Argentina"), "difficulty": 2, "url": ""},
# {"name": ("Bangladesh"), "difficulty": 2, "url": ""},
# {"name": ("Bosnia and Herzegovina"), "difficulty": 2, "url": ""},
# {"name": ("Botswana"), "difficulty": 2, "url": ""},
# {"name": ("Cambodia"), "difficulty": 2, "url": ""},
# {"name": ("Chile"), "difficulty": 2, "url": ""},
# {"name": ("Colombia"), "difficulty": 2, "url": ""},
# {"name": ("Costa Rica"), "difficulty": 2, "url": ""},
# {"name": ("Croatia"), "difficulty": 2, "url": ""},
# {"name": ("Cuba"), "difficulty": 2, "url": ""},
# {"name": ("Cyprus"), "difficulty": 2, "url": ""},
# {"name": ("Czech Republic","Czechia"), "difficulty": 2, "url": ""},
# {"name": ("North Korea","Democratic People's Republic of Korea"), "difficulty": 2, "url": ""},
# {"name": ("Egypt"), "difficulty": 2, "url": ""},
# {"name": ("Estonia"), "difficulty": 2, "url": ""},
# {"name": ("Ethiopia"), "difficulty": 2, "url": ""},
# {"name": ("Greece"), "difficulty": 2, "url": ""},
# {"name": ("Honduras"), "difficulty": 2, "url": ""},
# {"name": ("Hungary"), "difficulty": 2, "url": ""},
# {"name": ("Iran"), "difficulty": 2, "url": ""},
# {"name": ("Iraq"), "difficulty": 2, "url": ""},
# {"name": ("Jamaica"), "difficulty": 2, "url": ""},
# {"name": ("Kenya"), "difficulty": 2, "url": ""},
# {"name": ("Kuwait"), "difficulty": 2, "url": ""},
# {"name": ("Latvia"), "difficulty": 2, "url": ""},
# {"name": ("Lebanon"), "difficulty": 2, "url": ""},
# {"name": ("Liberia"), "difficulty": 2, "url": ""},
# {"name": ("Liechtenstein"), "difficulty": 2, "url": ""},
# {"name": ("Lithuania"), "difficulty": 2, "url": ""},
# {"name": ("Luxembourg"), "difficulty": 2, "url": ""},
# {"name": ("Malaysia"), "difficulty": 2, "url": ""},
# {"name": ("Monaco"), "difficulty": 2, "url": ""},
# {"name": ("Morocco"), "difficulty": 2, "url": ""},
# {"name": ("Myanmar"), "difficulty": 2, "url": ""},
# {"name": ("Namibia"), "difficulty": 2, "url": ""},
# {"name": ("Nauru"), "difficulty": 2, "url": ""},
# {"name": ("Nepal"), "difficulty": 2, "url": ""},
# {"name": ("Nicaragua"), "difficulty": 2, "url": ""},
# {"name": ("Niger"), "difficulty": 2, "url": ""},
# {"name": ("Nigeria"), "difficulty": 2, "url": ""},
# {"name": ("North Macedonia"), "difficulty": 2, "url": ""},
# {"name": ("Oman"), "difficulty": 2, "url": ""},
# {"name": ("Pakistan"), "difficulty": 2, "url": ""},
# {"name": ("Panama"), "difficulty": 2, "url": ""},
# {"name": ("Papua New Guinea"), "difficulty": 2, "url": ""},
# {"name": ("Peru"), "difficulty": 2, "url": ""},
# {"name": ("Philippines"), "difficulty": 2, "url": ""},
# {"name": ("Qatar"), "difficulty": 2, "url": ""},
# {"name": ("Moldova"), "difficulty": 2, "url": ""},
# {"name": ("Romania"), "difficulty": 2, "url": ""},
# {"name": ("Rwanda"), "difficulty": 2, "url": ""},
# {"name": ("Saudi Arabia"), "difficulty": 2, "url": ""},
# {"name": ("Serbia"), "difficulty": 2, "url": ""},
# {"name": ("Seychelles"), "difficulty": 2, "url": ""},
# {"name": ("Singapore"), "difficulty": 2, "url": ""},
# {"name": ("Slovakia"), "difficulty": 2, "url": ""},
# {"name": ("Slovenia"), "difficulty": 2, "url": ""},
# {"name": ("Somalia"), "difficulty": 2, "url": ""},
# {"name": ("Sri Lanka"), "difficulty": 2, "url": ""},
# {"name": ("Syria"), "difficulty": 2, "url": ""},
# {"name": ("Thailand"), "difficulty": 2, "url": ""},
# {"name": ("Uganda"), "difficulty": 2, "url": ""},
# {"name": ("United Arab Emirates","UAE"), "difficulty": 2, "url": ""},
# {"name": ("Uruguay"), "difficulty": 2, "url": ""},
# {"name": ("Venezuela"), "difficulty": 2, "url": ""},
# {"name": ("Vietnam","Viet Nam"), "difficulty": 2, "url": ""},
# ]
#
# hard_flags = [
# {"name": ("Afghanistan"), "difficulty": 3, "url": ""},
# {"name": ("Andorra"), "difficulty": 3, "url": ""},
# {"name": ("Angola"), "difficulty": 3, "url": ""},
# {"name": ("Antigua"), "difficulty": 3, "url": ""},
# {"name": ("Armenia"), "difficulty": 3, "url": ""},
# {"name": ("Azerbaijan"), "difficulty": 3, "url": ""},
# {"name": ("The Bahamas","Bahamas"), "difficulty": 3, "url": ""},
# {"name": ("Bahrain"), "difficulty": 3, "url": ""},
# {"name": ("Barbados"), "difficulty": 3, "url": ""},
# {"name": ("Belarus"), "difficulty": 3, "url": ""},
# {"name": ("Belize"), "difficulty": 3, "url": ""},
# {"name": ("Benin"), "difficulty": 3, "url": ""},
# {"name": ("Bhutan"), "difficulty": 3, "url": ""},
# {"name": ("Bolivia"), "difficulty": 3, "url": ""},
# {"name": ("Brunei"), "difficulty": 3, "url": ""},
# {"name": ("Bulgaria"), "difficulty": 3, "url": ""},
# {"name": ("Burkina Faso"), "difficulty": 3, "url": ""},
# {"name": ("Burundi"), "difficulty": 3, "url": ""},
# {"name": ("Cape Verde","Cabo Verde"), "difficulty": 3, "url": ""},
# {"name": ("Cameroon"), "difficulty": 3, "url": ""},
# {"name": ("Central African Republic","CAR"), "difficulty": 3, "url": ""},
# {"name": ("Chad"), "difficulty": 3, "url": ""},
# {"name": ("Comoros"), "difficulty": 3, "url": ""},
# {"name": ("Republic of the Congo","Republic of Congo","Congo Republic"), "difficulty": 3, "url": ""},
# {"name": ("Ivory Coast","Côte d'Ivoire","Cote d'Ivoire"), "difficulty": 3, "url": ""},
# {"name": ("Democratic Republic of the Congo","the Congo","Congo"), "difficulty": 3, "url": ""},
# {"name": ("Djibouti"), "difficulty": 3, "url": ""},
# {"name": ("Dominica"), "difficulty": 3, "url": ""},
# {"name": ("Dominican Republic","the Dominican Republic"), "difficulty": 3, "url": ""},
# {"name": ("Ecuador"), "difficulty": 3, "url": ""},
# {"name": ("El Salvador"), "difficulty": 3, "url": ""},
# {"name": ("Equatorial Guinea"), "difficulty": 3, "url": ""},
# {"name": ("Eritrea"), "difficulty": 3, "url": ""},
# {"name": ("Eswatini"), "difficulty": 3, "url": ""},
# {"name": ("Fiji"), "difficulty": 3, "url": ""},
# {"name": ("Gabon"), "difficulty": 3, "url": ""},
# {"name": ("The Gambia","Gambia"), "difficulty": 3, "url": ""},
# {"name": ("Georgia"), "difficulty": 3, "url": ""},
# {"name": ("Ghana"), "difficulty": 3, "url": ""},
# {"name": ("Grenada"), "difficulty": 3, "url": ""},
# {"name": ("Guatemala"), "difficulty": 3, "url": ""},
# {"name": ("Guinea"), "difficulty": 3, "url": ""},
# {"name": ("Guinea-Bissau","Guinea Bissau"), "difficulty": 3, "url": ""},
# {"name": ("Guyana"), "difficulty": 3, "url": ""},
# {"name": ("Haiti"), "difficulty": 3, "url": ""},
# {"name": ("Jordan"), "difficulty": 3, "url": ""},
# {"name": ("Kazakhstan"), "difficulty": 3, "url": ""},
# {"name": ("Kiribati"), "difficulty": 3, "url": ""},
# {"name": ("Kyrgyzstan"), "difficulty": 3, "url": ""},
# {"name": ("Laos","Lao"), "difficulty": 3, "url": ""},
# {"name": ("Lesotho"), "difficulty": 3, "url": ""},
# {"name": ("Libya"), "difficulty": 3, "url": ""},
# {"name": ("Madagascar"), "difficulty": 3, "url": ""},
# {"name": ("Malawi"), "difficulty": 3, "url": ""},
# {"name": ("Maldives"), "difficulty": 3, "url": ""},
# {"name": ("Mali"), "difficulty": 3, "url": ""},
# {"name": ("Malta"), "difficulty": 3, "url": ""},
# {"name": ("Marshall Islands"), "difficulty": 3, "url": ""},
# {"name": ("Mauritania"), "difficulty": 3, "url": ""},
# {"name": ("Mauritius"), "difficulty": 3, "url": ""},
# {"name": ("Federated States of Micronesia","Micronesia"), "difficulty": 3, "url": ""},
# {"name": ("Mongolia"), "difficulty": 3, "url": ""},
# {"name": ("Montenegro"), "difficulty": 3, "url": ""},
# {"name": ("Mozambique"), "difficulty": 3, "url": ""},
# {"name": ("Palau"), "difficulty": 3, "url": ""},
# {"name": ("Paraguay"), "difficulty": 3, "url": ""},
# {"name": ("Saint Kitts and Nevis","St. Kitts and Nevis"), "difficulty": 3, "url": ""},
# {"name": ("Saint Lucia","St. Lucia"), "difficulty": 3, "url": ""},
# {"name": ("Saint Vincent and the Grenadines","St. Vincent and the Grenadines"), "difficulty": 3, "url": ""},
# {"name": ("Samoa"), "difficulty": 3, "url": ""},
# {"name": ("San Marino"), "difficulty": 3, "url": ""},
# {"name": ("São Tomé and Príncipe","Sao Tome and Principe"), "difficulty": 3, "url": ""},
# {"name": ("Senegal"), "difficulty": 3, "url": ""},
# {"name": ("Sierra Leone"), "difficulty": 3, "url": ""},
# {"name": ("Solomon Islands"), "difficulty": 3, "url": ""},
# {"name": ("South Sudan"), "difficulty": 3, "url": ""},
# {"name": ("Sudan"), "difficulty": 3, "url": ""},
# {"name": ("Suriname"), "difficulty": 3, "url": ""},
# {"name": ("Tajikistan"), "difficulty": 3, "url": ""},
# {"name": ("East Timor","Timor-Leste"), "difficulty": 3, "url": ""},
# {"name": ("Togo"), "difficulty": 3, "url": ""},
# {"name": ("Tonga"), "difficulty": 3, "url": ""},
# {"name": ("Trinidad and Tobago"), "difficulty": 3, "url": ""},
# {"name": ("Tunisia"), "difficulty": 3, "url": ""},
# {"name": ("Turkmenistan"), "difficulty": 3, "url": ""},
# {"name": ("Tuvalu"), "difficulty": 3, "url": ""},
# {"name": ("Tanzania","United Republic of Tanzania"), "difficulty": 3, "url": ""},
# {"name": ("Uzbekistan"), "difficulty": 3, "url": ""},
# {"name": ("Vanuatu"), "difficulty": 3, "url": ""},
# {"name": ("Yemen"), "difficulty": 3, "url": ""},
# {"name": ("Zambia"), "difficulty": 3, "url": ""},
# {"name": ("Zimbabwe"), "difficulty": 3, "url": ""}
# ]
