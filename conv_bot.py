from pytube import YouTube
import os
import telebot

bot = telebot.TeleBot(API_TOKEN)


# Say hello to user
@bot.message_handler(commands=['start'])
def shoot(message):
    bot.send_message(message.chat.id, "Да ссылку Youtube!")


# Take link of youtube video and give user mp3 file
@bot.message_handler()
def run(message):
    link = message.text
    try:
        filename = download_mp3(link)
        bot.send_audio(message.chat.id, audio=open(filename, 'rb'))
        os.remove(filename)
    except:
        bot.send_message(message.chat.id, "Извините. Что-то пошло не так.")


def download_mp3(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    print(new_file + " has been successfully downloaded.")
    return new_file


if __name__ == '__main__':
    bot.polling()
