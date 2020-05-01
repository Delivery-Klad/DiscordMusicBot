import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os

TOKEN = 'NjI4MjA4MzgyNzU0NDIyNzg0.XZJuUA.-BdO22-ECHYjBCPp4eoLh5OMKGk'
BOT_PREFIX = '.'

bot = commands.Bot(command_prefix=BOT_PREFIX)


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")


@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        return await voice.move_to(channel)

    await channel.connect()
    await ctx.send(f"Бот подключился к {channel}")
    print(f"Бот подключился к {channel}\n")


@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"Бот оключился от {channel}")
        await ctx.send(f"Бот оключился от {channel}")
    else:
        print("Бот не находится в голосовом канале")
        await ctx.send("Бот не находится в голосовом канале")


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        print("ERROR: Что-то играет")
        await ctx.send("ERROR: Что-то играет")
        return

    await ctx.send("Начинаю загрузку...")

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
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("выполнено"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Сейчас проигрывается: {nname[0]}")


bot.run(TOKEN)
