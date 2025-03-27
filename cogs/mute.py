import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from discord.utils import get

with open('setting.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile)  

class mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="mute",description="禁言")
    @commands.has_role("admin")
    async def mute(self,interation, member : discord.Member ,reason:str=None):
        try:
            if reason == None:
                reason = "無"
            role = discord.utils.get(interation.guild.roles, name="Muted")
            await member.add_roles(role,reason=None,atomic=True)
            await interation.response.send_message(f"{member.mention}嘴巴閉閉 <3，因為{reason}")
        except Exception as err:
                print(err)

    @app_commands.command(name="unmute",description="解除禁言")
    @commands.has_role("admin")
    async def unmute(self,interation, member : discord.Member ,reason:str=None):
        try:
            if reason == None:
                reason = "無"
            role = discord.utils.get(interation.guild.roles, name='Muted')
            await member.remove_roles(role,reason=None,atomic=True)
            await interation.response.send_message(f"{member.mention}嘴巴開開 <3，因為{reason}")
        except Exception as err:
                print(err)


    


async def setup(bot: commands.Bot):
    await bot.add_cog(mute(bot))