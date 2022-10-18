from pytube import YouTube
import os
import telebot
import subprocess
import math
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from config import API_TOKEN


bot = telebot.TeleBot(API_TOKEN)


# Приветствуем пользователя
@bot.message_handler(commands=['start'])
def shoot(message):
    bot.send_message(message.chat.id, "Дай ссылку Youtube!")


# Берем Youtube ссылку из сообщения пользователя
@bot.message_handler()
def run(message):
    link = message.text     # Ссылка из сообщения пользователя
    
    filename = download_mp4(link)       # Скачиваем файл в формате mp4
    file_size = os.stat(filename).st_size / (1024 * 1024)       # Определяем размер файла
    if file_size < 50:
        bot_send_message(filename, message)
    else:
        filenames = split_video(filename, file_size)
        for filename in filenames:
            bot_send_message(filename, message)


def bot_send_message(filename, message):
    filename = convert_to_mp3(filename)
    bot.send_audio(message.chat.id, audio=open(filename, 'rb'))
    os.remove(filename)


def download_mp4(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    return video.download()


def convert_to_mp3(out_file):
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def split_video(filename, file_size):
    timesplit = math.ceil(file_size/45)
    videoLength = get_length(filename)
    splitLength = videoLength/timesplit
    starttime = [i * splitLength for i in range(timesplit)]
    endtime = [(i+1) * splitLength for i in range(timesplit)]
    filenames = []
    base, _ = os.path.splitext(filename)
    for i in range(timesplit):
        targetname = f'{base}_part{i + 1}.mp4'
        ffmpeg_extract_subclip(filename, starttime[i], endtime[i], targetname=targetname)
        filenames.append(targetname)
    os.remove(filename)
    return filenames



if __name__ == '__main__':
    bot.polling()
