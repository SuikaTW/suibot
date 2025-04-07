import discord
from discord import app_commands
from discord.ext import commands
import json
<<<<<<< HEAD
from bot import SETTINGS_FILE

with open(SETTINGS_FILE, mode="r", encoding='utf8') as jfile:
=======

with open('setting.json', mode="r", encoding='utf8') as jfile:  
>>>>>>> f503b7b0abf8de020e728e7fef2c8e9fc9266158
    jdata = json.load(jfile)  

class button(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 抓對應函式    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
<<<<<<< HEAD
        if interaction.type == discord.InteractionType.component and "custom_id" in interaction.data:
            custom_id = interaction.data["custom_id"]
            # 處理有 custom_id 的互動
            if custom_id == "example_button":
                await interaction.response.send_message("按鈕被點擊！")
        else:
            # 忽略或記錄無 custom_id 的互動
            print("⚠ 無法處理此互動，缺少 custom_id！")
=======
        # 確認互動類型是否為按鈕
        if interaction.type == discord.InteractionType.component and "custom_id" in interaction.data:
            if interaction.data["custom_id"] == "csleep":
                await interaction.response.send_message(jdata['pic'])
            elif interaction.data["custom_id"] == "jodieride":
                await interaction.response.send_message(jdata['bro'])
        else:
            # 忽略非按鈕的互動
            return
>>>>>>> f503b7b0abf8de020e728e7fef2c8e9fc9266158

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
<<<<<<< HEAD

    @discord.ui.button(label="按鈕範例", style=discord.ButtonStyle.primary, custom_id="example_button")
    async def example_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("按鈕被點擊！")

class ExampleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="選項 1", value="option_1"),
            discord.SelectOption(label="選項 2", value="option_2"),
        ]
        super().__init__(placeholder="選擇一個選項", options=options, custom_id="example_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"你選擇了：{self.values[0]}")
=======
>>>>>>> f503b7b0abf8de020e728e7fef2c8e9fc9266158

async def setup(bot: commands.Bot):
    await bot.add_cog(button(bot))