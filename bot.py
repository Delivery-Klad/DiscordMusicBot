import discord
import shutil
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
from os import system
import asyncio

BOT_PREFIX = '.'
bot = commands.Bot(command_prefix=BOT_PREFIX)


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")
    game = discord.Game("поиск дома")
    await bot.change_presence(activity=game)


@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    """Подключиться к текущему голосовому каналу"""
    try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            return await voice.move_to(channel)

        await channel.connect()
        await ctx.send(f"Бот подключился к {channel}")
        print(f"Бот подключился к {channel}\n")
    except Exception as e:
        await ctx.send(f"Пользователь не в голосовом канале")
        print(f"Пользователь не в голосовом канале\n")


@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    """Отключиться от текущего голосового канала"""
    try:
        channel = ctx.message.author.voice.channel
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            print(f"Бот оключился от {channel}")
            await ctx.send(f"Бот оключился от {channel}")
        else:
            print("Бот не находится в голосовом канале")
            await ctx.send("Бот не находится в голосовом канале")
    except Exception as e:
        print("Бот не находится в голосовом канале")
        await ctx.send("Бот не находится в голосовом канале")


@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):
    """Приостановить воспроизведение"""
    try:
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Пауза")
            voice.pause()
            await ctx.send("Воспроизведение приостановлено")
        else:
            print("нечего ставить на паузу")
            await ctx.send("Нечего ставить на паузу")
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):
    """Продолжить воспроизведение"""
    try:
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_paused():
            print("продолжение")
            voice.resume()
            await ctx.send("Продолжаю воспроизведение")
        else:
            print("ERROR")
            await ctx.send("ERROR")
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, volume: int):
    """Изменение громкости (.volume 50)"""
    try:
        if ctx.voice_client is None:
            return await ctx.send("Бот не находится в голосовом канале")
        if volume < 0 or volume > 200:
            await ctx.send(f"{ctx.author.mention} Беда с башкой?")
            return
        print(volume / 100)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Громкость: {volume}%")
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['c', 'cle'])
async def clear(ctx):
    """Очистить очередь"""
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("Очередь очищена")
        voice.stop()
        await ctx.send("Очередь очищена")
    else:
        print("Очередь пуста")
        await ctx.send("Очередь пуста")


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, *url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("Очередь пуста\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Воспроизвожу следующий трек\n")
                print(f"Треки в очереди: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()


    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Удаление старого файла")
    except PermissionError:
        print("Что-то играет")
        await ctx.send("ERROR: Что-то играет, используйте (queue youtubeURL) чтобы добавить в очередь")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Удаление старого расположения очереди")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Начинаю загрузку")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("загрузка\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' + c_path + '"' + " -s " + song_search)

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07


queues = {}


@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, *url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + song_search)

    await ctx.send("Трек добвлен в очередь, его позиция: " + str(q_num))
    print("Трек добавлен в очередь\n")


@bot.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    try:
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Воспроизведение следующего трека")
            voice.stop()
            await ctx.send("Воспроизвожу следующий трек")
        else:
            print("Нечего воспроизводить")
            await ctx.send("Список воспроизведения подошел к концу")
    except Exception as e:
        print("Нечего воспроизводить")
        await ctx.send("Список воспроизведения подошел к концу ")


b_token = os.environ.get('TOKEN')
bot.run(str(b_token))
