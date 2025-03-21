import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from core.protect import Protect, find_token
from discord.utils import get

with open('setting.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile)  

class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        benny = ['bj','BJ','奔尼眷','BennyJeng','bennyjeng','benny','Benny','Bennyjeng'] 
        if message.author == self.bot.user:
            return
        if message.content in benny:
            await message.channel.send("BennyJeng... BENNYJENG IS REAL!!!")
            await message.channel.send(jdata['bjgif'])

        if message.author == self.bot.user:
            return
        if message.content == '陳盡心':
            await message.channel.send("噁心")
                    
        if find_token(message.content):
            await message.delete()
            await message.channel.send("你不能輸入 Token！")
    
        
    
    
        

async def setup(bot: commands.Bot):
    await bot.add_cog(event(bot))