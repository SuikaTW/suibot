import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command

from core.cogs import Cog_Extention
from bot import SETTINGS_FILE

with open(SETTINGS_FILE,mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile)  


class react(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="picture",description="傳送照片")                                  
    async def picture(self,interaction):    
            await interaction.response.send_message(jdata['pic'])  
    

async def setup(bot: commands.Bot):
    await bot.add_cog(react(bot))