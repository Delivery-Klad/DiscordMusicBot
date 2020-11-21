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
current_index = 1
volumes = 15
queues = []
PlayLst = ['https://www.youtube.com/watch?v=yNC0p2RXeXM', 'https://www.youtube.com/watch?v=7tThYxp5kmk']


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
            print("Нечего ставить на паузу")
            await ctx.send("Нечего ставить на паузу")
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):
    """Продолжить воспроизведение"""
    try:
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            print("Продолжение")
            voice.resume()
            await ctx.send("Продолжаю воспроизведение")
        else:
            print("ERROR")
            await ctx.send("ERROR")
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, vol: int):
    """Изменение громкости (.volume 50)"""
    try:
        global volumes
        if ctx.voice_client is None:
            return await ctx.send("Бот не находится в голосовом канале")
        if vol < 0 or vol > 200:
            await ctx.send(f"{ctx.author.mention} Беда с башкой?")
            return
        print(vol / 100)
        ctx.voice_client.source.volume = vol / 100
        await ctx.send(f"Громкость: {vol}%")
        volumes = vol
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['c', 'clr'])
async def clear(ctx):
    """Очистить очередь воспроизведения"""
    global volumes
    voice = get(bot.voice_clients, guild=ctx.guild)
    queues.clear()
    volumes = 15
    if voice and voice.is_playing():
        print("Очередь очищена")
        voice.stop()
        await ctx.send("Очередь очищена")
    else:
        print("Очередь пуста")
        await ctx.send("Очередь пуста")
        
        
@bot.command(pass_context=True, aliases=['li', 'lst'])
async def list(ctx):
    """Запустить проигрывание плэйлиста"""
    for i in PlayLst:
        queues.append(i)
    await ctx.send(str(queues)) 
         

@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, *url: str):
    """Воспроизвести трек (URL или название)"""
    global volumes
    queues.append(url)

    def check_queue():
        global current_index
        Queue_infile = len(queues)
        if Queue_infile > 0:
            if current_index >= len(queues):
                current_index = 0
            url = queues[current_index]
            print(queues)
            current_index += 1
            song_there = os.path.isfile("song.mp3")
            try:
                if song_there:
                    os.remove("song.mp3")
                    print("Удаление старого файла")
            except PermissionError:
                print("Что-то играет")
                return
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
                    print("Загрузка\n")
                    ydl.download([f"ytsearch1:{song_search}"])
            except:
                print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
                c_paths = os.path.dirname(os.path.realpath(__file__))
                system("spotdl -ff song -f " + '"' + c_paths + '"' + " -s " + song_search)

            voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = volumes / 100
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
            print("Загрузка\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' + c_path + '"' + " -s " + song_search)
    queues.append(url)
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = volumes / 100


@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, *url: str):
    """Добавление трека в очередь"""
    queues.append(url)
    print(queues)
    await ctx.send("Трек добвлен в очередь, его позиция: " + str(len(queues)))
    print("Трек добавлен в очередь его позиция: {0}\n".format(len(queues)))


@bot.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    """Переключение трека"""
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
