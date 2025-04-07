import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from core.protect import Protect
from bot import SETTINGS_FILE

from core.cogs import Cog_Extention

with open(SETTINGS_FILE, mode="r", encoding='utf8') as jfile:
    jdata = json.load(jfile)  

num = 0

class main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name = "clhs",description="傳送中壢高中官網")                                  
    async def clhs(self,interaction:discord.Interaction):
        await interaction.response.send_message('https://www.clhs.tyc.edu.tw/home')

    @app_commands.command(name = "hello",description="跟你說哈囉")
    async def hello(self,interaction:discord.Interaction):
        await interaction.response.send_message('Hello!!')
        await interaction.channel.send('<:SPOILER_unknown:1353774295863529523>')
    
    @app_commands.command(name="say",description="匿名留言")
    async def say(self, interaction: discord.Interaction, msg: str):   
            message = Protect.message(msg)
            await interaction.channel.send(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(main(bot))