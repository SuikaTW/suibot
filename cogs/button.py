import discord
from discord import app_commands
from discord.ext import commands
import json

with open('setting.json', mode="r", encoding='utf8') as jfile:  
    jdata = json.load(jfile)  

class button(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 抓對應函式    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # 確認互動類型是否為按鈕
        if interaction.type == discord.InteractionType.component and "custom_id" in interaction.data:
            if interaction.data["custom_id"] == "csleep":
                await interaction.response.send_message(jdata['pic'])
            elif interaction.data["custom_id"] == "jodieride":
                await interaction.response.send_message(jdata['bro'])
        else:
            # 忽略非按鈕的互動
            return

    @app_commands.command(name="cpic", description="叫出一些照片")
    async def view(self, interaction: discord.Interaction):
        """顯示按鈕"""
        view = discord.ui.View()
        
        button_view = discord.ui.Button(
            custom_id="csleep",
            label='sleep',
            style=discord.ButtonStyle.blurple
        )
        
        button_view2 = discord.ui.Button(
            custom_id="jodieride",
            label='bro',
            style=discord.ButtonStyle.blurple
        )
        
        view.add_item(button_view)
        view.add_item(button_view2)

        await interaction.response.send_message(view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(button(bot))