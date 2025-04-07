import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from discord.utils import get


class role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="add_role",description="新增身分組")
    @commands.has_role("admin")
    async def addrole(self,interation, member : discord.Member, role : discord.Role):
        try:
            await member.add_roles(role,reason=None,atomic=True)
            await interation.response.send_message(f"{member.mention}獲得了{role}")
        except Exception as err:
                print(err)
    
    @app_commands.command(name="remove_role",description="移除身分組")
    @commands.has_role("admin")
    async def removerole(self,interation, member : discord.Member, role : discord.Role):
        try:
            await member.remove_roles(role,reason=None,atomic=True)
            await interation.response.send_message(f"{member.mention}失去了{role}")
        except Exception as err:
                print(err)

async def setup(bot: commands.Bot):
    await bot.add_cog(role(bot))