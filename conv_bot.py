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
    try:
        if file_size < 50:       # Если размер меньше 50 мб, то отправдяем файл, как есть (ограничение телеграма). В противном случае отправляем файл по частям
            bot_send_message(filename, message)
        else:
            filenames = split_video(filename, file_size)
            for filename in filenames:
                bot_send_message(filename, message)
    except:
        bot.send_message(message.chat.id, "Извините. Что-то пошло не так.")
    

# Отправка аудиофайла 
def bot_send_message(filename, message):
    filename = convert_to_mp3(filename)
    bot.send_audio(message.chat.id, audio=open(filename, 'rb'))
    os.remove(filename)

# Скачиваем видео файл в формате mp4 
def download_mp4(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    return video.download()

# Конвертируем в mp3
def convert_to_mp3(out_file):
    base, ext = os.path.splitext(out_file)      # Отделяем название файла от расширения
    new_file = base + '.mp3'        # Формируем название файла
    os.rename(out_file, new_file)       # Переименовываем файл
    return new_file

# Получаем продолжительность видео файла
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

# Делим файл на части
def split_video(filename, file_size):
    timesplit = math.ceil(file_size/45)     # Определяем на какое количество файлов надо делить. Делим размер файла на 45 и округляем в большую сторону.
    videoLength = get_length(filename)      
    splitLength = videoLength/timesplit     # Получаем промежутки времени, на которые надо делить
    starttime = [i * splitLength for i in range(timesplit)]     # Список начала временных отрезков
    endtime = [(i+1) * splitLength for i in range(timesplit)]       # Список концовок временных отрезков
    filenames = []      # Список для сохранения названий файлов
    base, _ = os.path.splitext(filename)
    for i in range(timesplit):
        targetname = f'{base}_part{i + 1}.mp4'      # Формирование названия файла
        ffmpeg_extract_subclip(filename, starttime[i], endtime[i], targetname=targetname)       # Деление файла по времени
        filenames.append(targetname)
    os.remove(filename)     # Удаление исходного файла
    return filenames

if __name__ == '__main__':
    bot.polling()
