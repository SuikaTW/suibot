import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from discord.utils import get

count1 = 0
count2 = 0
num = 0

with open('setting.json',mode= "r",encoding='utf8') as jfile:  
    jdata = json.load(jfile)  

class order(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #抓對應函式    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
    
        if interaction.data["custom_id"] == "order1":
            global count1
            count1 += 1
            await interaction.response.send_message(f"百Q{count1}份")
                
        if interaction.data["custom_id"] == "order2":
            global count2
            count2 += 1
            await interaction.response.send_message(f"O奶{count2}份")  

        if interaction.data["custom_id"] == "reset":
            if count1 != 0:
                print ("百Q 共",count1,"份")
            if count2 != 0:
                print ("O奶 共",count2,"份")

            count1 = 0
            count2 = 0
            global num 
            num += 1
            await interaction.response.send_message(f"已送出訂單，編號為{num}")
            print("訂單編號為",num) 
        
    @app_commands.command(name = "order",description="order meal")
    async def order(self,interaction:discord.Interaction):
            view = discord.ui.View()
            
            button_view = discord.ui.Button(
                custom_id="order1",
                label='百Q',
                style= discord.ButtonStyle.blurple)
            
            button_view2 = discord.ui.Button(
                custom_id="order2",
                label='O奶',
                style= discord.ButtonStyle.blurple)
            
            button_view3 = discord.ui.Button(
                custom_id="reset",
                label='送出',
                style= discord.ButtonStyle.green)

            
            view.add_item(button_view)
            view.add_item(button_view2)
            view.add_item(button_view3)

            await interaction.response.send_message(view = view)
    

    @app_commands.command(name="menu",description="show menu")
    async def menu(self,interation:discord.Interaction):
    
        embed=discord.Embed(title="菜單", color=0x5d9ef4)
        embed.add_field(name="百香QQ綠", value=45, inline=True)
        embed.add_field(name="Oreo奶茶", value=45, inline=True)
        await interation.response.send_message(embed=embed)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(order(bot))