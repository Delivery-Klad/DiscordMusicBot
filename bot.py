import discord
import youtube_dl
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio

bot = commands.Bot(command_prefix='.')
vol = 100


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")
    game = discord.Game("поиск дома")
    await bot.change_presence(activity=game)


@bot.command(name='ping', help='Проверить пинг')
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)}ms')


@bot.command(pass_context=True, brief="Пригласить бота в канал", aliases=['jo', 'joi'])
async def join(ctx):
    try:
        channel = ctx.message.author.voice.channel
    except AttributeError:
        await ctx.send("Вы должны быть в голосовом канале")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(f"Подключен к каналу: {channel}")


@bot.command(pass_context=True, brief="Отключить бота от канала", aliases=['le', 'lea'])
async def leave(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send("Бот отключен от канала")
    else:
        await ctx.send("Бот не подключен к голосовому каналу")


@bot.command(pass_context=True, brief="Включить проигрывание 'play [url]'", aliases=['pl', 'pla'])
async def play(ctx, *, url: str):
    global vol
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Подождите завершения песни или воспользуйтесь командой <skip>")
        return
    await ctx.send("Loading...")

    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        await ctx.send("Не в голосовом канале")
        return
    print(url)
    if "spotify" in url and "playlist" in url:
        pass
    if "spotify" in url:
        os.system(f"spotdl {url}")
    else:
        ydl_opts = {
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',

            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(str(url))
    for file in os.listdir("./"):
        print(file)
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    voice.volume = vol
    voice.is_playing()
    await ctx.send(f"Проигрывание запущено")


@bot.command(pass_context=True, brief="Поставить проигрывание на паузу", aliases=['pa', 'pau'])
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Проигрывание приостановлено")
    else:
        await ctx.send("В данный момент ничего не проигрывается")


@bot.command(pass_context=True, brief="Продолжить воспроизведение", aliases=['r', 'res'])
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Воспроизведение продолжено")
    else:
        await ctx.send("В данный момент нет приостановленного трека")


@bot.command(pass_context=True, brief="Скипнуть трек", aliases=['sk', 'ski'])
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Трек пропущен, а ты попущен")
    else:
        await ctx.send("Нечего скипать")


b_token = os.environ.get('TOKEN')
bot.run(str(b_token))
