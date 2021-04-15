import discord
import youtube_dl
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system

bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    print('Logged')


@bot.command()
async def say(ctx, *, msg):
    await ctx.channel.purge(limit=1)
    await ctx.send(msg)


@bot.command(pass_context=True, brief="Пригласить бота в канал", aliases=['jo', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("Вы должны быть в голосовом канале")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
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
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("А, ОЙ! Ошиб04ка")
        return
    await ctx.send("Подождите завершения песни или воспользуйтесь командой <skip>")

    voice = get(bot.voice_clients, guild=ctx.guild)

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
        # r = ydl.extract_info(url ,download=False)
        # r = ydl.extract_info(f"ytsearch:'{url}'", download=False)
        ydl.download([url])

        # print(str(url))
        title = r["title"]
        print(title)

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    voice.volume = 100
    voice.is_playing()
    await ctx.send(f"Проигрывается: " + title)


@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Проигрывание приостановлено")
    else:
        await ctx.send("В данный момент ничего не проигрывается")


@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Воспроизведение продолжено")
    else:
        await ctx.send("В данный момент нет приостановленного трека")


@bot.command(pass_context=True, aliases=['sk', 'ski'])
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Трек пропущен")
    else:
        await ctx.send("Нечего скипать")


b_token = os.environ.get('TOKEN')
bot.run(str(b_token))
