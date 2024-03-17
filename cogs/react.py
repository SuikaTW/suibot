import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command

from core.cogs import Cog_Extention

with open('setting.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile)  


class react(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="picture",description="send a pic")                                  
    async def picture(self,interaction):
        try:        
            await interaction.response.send_message(jdata['pic'])  
        except Exception as err:
            print(err)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(react(bot))