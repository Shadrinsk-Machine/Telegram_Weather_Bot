import os
import requests
from dotenv import load_dotenv
from aiogram.types import ContentType
from aiogram import types
from load import bot, dp
import db

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
weather_token = os.getenv("weather_token")


def do_req(city: str) -> dict | bool:
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}"
            f"&units=metric")
        if r.json()['cod'] == '404':
            return False
        return r.json()
    except Exception as ex:
        print(ex)
        return False


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=db.photo_id,
                         caption="This is the most genius bot ever\nWrite the city to see the weather")


@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_message(message: types.Message):
    await bot.send_voice(chat_id=message.from_user.id,
                         voice=db.voice_id)
    text = message.from_user.first_name + str(" @") + message.from_user.username + str(" sent a voice message:")
    await bot.send_message(chat_id=db.chat_id, text=text)
    await bot.send_voice(chat_id=db.chat_id, voice=message.voice.file_id)


@dp.message_handler()
async def get_weather(message: types.Message):
    data = do_req(message.text)
    if data:
        city = data['name']
        temp = data['main']['temp']
        wind = data['wind']['speed']
        weather_description = data['weather'][0]['main']
        if weather_description in db.smiles:
            wd = db.smiles[weather_description]
        else:
            wd = "Check the weather yourself, i can't figure it out"
        if city != 'Çanakkale Province':
            await message.answer(f"*{city}*\nThe weather is {wd}\nTemperature: {temp}C°\nWind: {wind} m/s\n",
                                 parse_mode="Markdown")
            await bot.send_sticker(chat_id=message.from_user.id, sticker=db.sticker1_id)
        else:
            await message.answer(
                "Why did you want to see the weather in the capital of the world ?\nThe weather is ideal anyway !")
            await bot.send_sticker(chat_id=message.from_user.id, sticker=db.sticker_id)
    else:
        await message.answer(f"What is this '{message.text}' ?\nPlease, write the correct city !\n")
    if message.from_user.username != 'Incredible_Genius':
        text = message.from_user.first_name + str(" @") + message.from_user.username + str(
            " sent the text:\n") + message.text
        await bot.send_message(chat_id=db.chat_id, text=text)


@dp.message_handler(content_types=[ContentType.ANY])
async def get_any(message: types.Message):
    await bot.forward_message(db.chat_id, message.from_user.id, message.message_id)
    await message.answer("Sorry, the owner of this bot has your data \U0001F643")
