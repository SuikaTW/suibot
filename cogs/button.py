import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command

with open('setting.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile)  

class button(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #抓對應函式    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] == "csleep":
            csleep = discord.File(jdata['csleep'])
            await interaction.response.send_message(file=csleep)
        if interaction.data["custom_id"] == "jodieride":
            jodieride = discord.File(jdata['jodieride'])
            await interaction.response.send_message(file=jodieride)     
            
    @app_commands.command(name = "cpic",description="call some picture")
    async def view(self,interaction:discord.Interaction):
            view = discord.ui.View()
            
            button_view = discord.ui.Button(
                custom_id="csleep",
                label='sleep',
                style= discord.ButtonStyle.blurple)
            
            button_view2 = discord.ui.Button(
                custom_id="jodieride",
                label='jodie',
                style= discord.ButtonStyle.blurple)
            
            view.add_item(button_view)
            view.add_item(button_view2)

            await interaction.response.send_message(view = view)

async def setup(bot: commands.Bot):
    await bot.add_cog(button(bot))