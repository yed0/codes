import aiogram
import os
import speech_recognition as ap
from pydub import AudioSegment
from aiogram import Dispatcher, Bot, types



Atoken = ""

bot = Bot(token=Atoken)
dp = Dispatcher()


def oga2wav(filename):
    new_filename = filename.replace(".oga", ".wav")
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format="wav")
    return new_filename


def recognize_speech(oga_filename):
    wav_filename = oga2wav(oga_filename)
    recognizer = ap.Recognizer()

    with ap.WavFile(wav_filename) as source:
        wav_audio = recognizer.record(source)

    text = recognizer.recognize_google(wav_audio, language = 'ru')

    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text


def download_file(bot, file_id):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename


@dp.message(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hello, send me an audio to get it translated")


@dp.message_handler(content_types = ['voice'])
async def transcript(message):
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    await message.reply(message.chat.id, text)


bot.polling()

