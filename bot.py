import discord
import shutil
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
from os import system

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
            await ctx.send("пауза")
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

        print(volume/100)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Громкость: {volume}%")
    except Exception as e:
        print('error')


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

    await ctx.send(f"Начинаю загрузку")
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("Уже что-то играет")
        return

    #await ctx.send("a")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Проигрывется: {nname[0]}")
    print("playing\n")
    
    
@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("становлено")
        voice.stop()
        await ctx.send("ВОспроизведение остановлено")
    else:
        print("Нечего останавливать")
        await ctx.send("Плейлист пуст")
    
    
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
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + song_search)

    await ctx.send("Добавление " + str(q_num) + " в очередь")
    print("Добавлено в очередь\n")
    
    
@bot.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    try:
        voice = get(bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Playing Next Song")
            voice.stop()
            await ctx.send("Next Song")
        else:
            print("Нечего воспроизводить")
            await ctx.send("Список воспроизведения подошел к концу")
    except Exception as e:
        print("Нечего воспроизводить")
        await ctx.send("Список воспроизведения подошел к концу")


b_token = os.environ.get('TOKEN')
bot.run(str(b_token))
