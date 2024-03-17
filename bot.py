import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
import os

with open('setting.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile) 

with open('token.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile) 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "=", intents = intents)

@bot.event
async def on_ready():
    await bot.tree.sync() #同步斜線指令到 Discord
    status_w = discord.Status.idle
    #這邊設定機器當前的狀態文字
    #type可以是playing（遊玩中）、streaming（直撥中）、listening（聆聽中）、watching（觀看中）、custom（自定義）
    activity_w = discord.Activity(type=discord.ActivityType.listening, name="西瓜一族")
    await bot.change_presence(status= status_w, activity=activity_w)
    print("ready")

# 載入指令程式檔案
@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Load {extension}")

# 卸載指令檔案
@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unload {extension}")

# 重新載入檔案
@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded {extension}")

# 載入全部程式檔案
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(jdata['token'])


if __name__ == "__main__":
    asyncio.run(main())
