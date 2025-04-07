import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from discord.utils import get

# 記數
count1 = 0
count2 = 0
count3 = 0
count4 = 0
count5 = 0
count6 = 0
num = 0

# 金額
hq = 45
om = 40
dog = 40
bmt = 40
bm = 50
yamg = 40
from bot import SETTINGS_FILE
with open(SETTINGS_FILE, mode="r", encoding='utf8') as jfile:
    jdata = json.load(jfile)

class order(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 抓對應函式
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if "custom_id" in interaction.data:
            custom_id = interaction.data["custom_id"]
            if custom_id == "order1":
                await interaction.response.send_message("百香QQ綠 1 份")
            elif custom_id == "order2":
                await interaction.response.send_message("Oreo奶茶 1 份")
        else:
            print("⚠ 無法處理此互動，缺少 custom_id！")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # 確認 interaction.data 是否包含 custom_id
        if "custom_id" in interaction.data:
            if interaction.data["custom_id"] == "order1":
                global count1
                count1 += 1
                await interaction.response.send_message(f"百香QQ綠 {count1} 份")

            elif interaction.data["custom_id"] == "order2":
                global count2
                count2 += 1
                await interaction.response.send_message(f"Oreo奶茶 {count2} 份")

            elif interaction.data["custom_id"] == "order3":
                global count3
                count3 += 1
                await interaction.response.send_message(f"多多綠茶 {count3} 份")

            elif interaction.data["custom_id"] == "order4":
                global count4
                count4 += 1
                await interaction.response.send_message(f"珍珠奶茶 {count4} 份")

            elif interaction.data["custom_id"] == "order5":
                global count5
                count5 += 1
                await interaction.response.send_message(f"珍珠鮮奶茶 {count5} 份")

            elif interaction.data["custom_id"] == "order6":
                global count6
                count6 += 1
                await interaction.response.send_message(f"椰果奶綠 {count6} 份")

            elif interaction.data["custom_id"] == "reset":
                embed = discord.Embed(title="您的訂單", color=0xfbff29)
                embed.set_thumbnail(url=jdata['sukaicon'])
                if count1 != 0:
                    embed.add_field(name="百香QQ綠", value=f"{count1} 份", inline=True)
                    print("百香QQ綠 共", count1, "份")
                if count2 != 0:
                    embed.add_field(name="Oreo奶茶", value=f"{count2} 份", inline=True)
                    print("Oreo奶茶 共", count2, "份")
                if count3 != 0:
                    embed.add_field(name="多多綠茶", value=f"{count3} 份", inline=True)
                    print("多多綠茶 共", count3, "份")
                if count4 != 0:
                    embed.add_field(name="珍珠奶茶", value=f"{count4} 份", inline=True)
                    print("珍珠奶茶 共", count4, "份")
                if count5 != 0:
                    embed.add_field(name="珍珠鮮奶茶", value=f"{count5} 份", inline=True)
                    print("珍珠鮮奶茶 共", count5, "份")
                if count6 != 0:
                    embed.add_field(name="椰果奶綠", value=f"{count6} 份", inline=True)
                    print("椰果奶綠 共", count6, "份")
                sum = count1 * hq + count2 * om + count3 * dog + count4 * bmt + count5 * bm + count6 * yamg
                count1 = 0
                count2 = 0
                count3 = 0
                count4 = 0
                count5 = 0
                count6 = 0
                global num
                num += 1
                print(f"金額為: {sum}")
                print("訂單編號為", num)
                print("-------------------")
                embed.add_field(name="總計", value=f"{sum} 元", inline=True)
                embed.set_footer(text=f"訂單編號: {num}")
                await interaction.channel.send(embed=embed)

            elif interaction.data["custom_id"] == "canc":
                count1 = 0
                count2 = 0
                count3 = 0
                count4 = 0
                count5 = 0
                count6 = 0
                await interaction.response.send_message(f"已取消訂單")
        else:
            # 如果沒有 custom_id，忽略或記錄
            print("⚠ 無法處理此互動，缺少 custom_id！")

    @app_commands.command(name="order", description="ˇ點餐")
    async def order(self, interaction: discord.Interaction):
        view = discord.ui.View()

        button_view = discord.ui.Button(
            custom_id="order1",
            label='百香QQ綠',
            style=discord.ButtonStyle.blurple)

        button_view2 = discord.ui.Button(
            custom_id="order2",
            label='Oreo奶茶',
            style=discord.ButtonStyle.blurple)

        button_view4 = discord.ui.Button(
            custom_id="order3",
            label='多多綠茶',
            style=discord.ButtonStyle.blurple)

        button_view5 = discord.ui.Button(
            custom_id="order4",
            label='珍珠奶茶',
            style=discord.ButtonStyle.blurple)

        button_view6 = discord.ui.Button(
            custom_id="order5",
            label='珍珠鮮奶茶',
            style=discord.ButtonStyle.blurple)

        button_view7 = discord.ui.Button(
            custom_id="order6",
            label='椰果奶綠',
            style=discord.ButtonStyle.blurple)

        button_view3 = discord.ui.Button(
            custom_id="reset",
            label='送出',
            style=discord.ButtonStyle.green)

        button_view8 = discord.ui.Button(
            custom_id="canc",
            label='取消',
            style=discord.ButtonStyle.red)

        view.add_item(button_view)
        view.add_item(button_view2)
        view.add_item(button_view4)
        view.add_item(button_view5)
        view.add_item(button_view6)
        view.add_item(button_view7)
        view.add_item(button_view3)
        view.add_item(button_view8)

        await interaction.response.send_message(view=view)

    @app_commands.command(name="menu", description="顯示菜單")
    async def menu(self, interation: discord.Interaction):
        embed = discord.Embed(title="菜單", color=0x5d9ef4)
        embed.set_thumbnail(url=jdata['sukaicon'])
        embed.add_field(name="百香QQ綠", value="$45", inline=True)
        embed.add_field(name="Oreo奶茶", value="$45", inline=True)
        embed.add_field(name="多多綠茶", value="$40", inline=True)
        embed.add_field(name="珍珠奶茶", value="$40", inline=True)
        embed.add_field(name="珍珠鮮奶茶", value="$50", inline=True)
        embed.add_field(name="椰果奶綠", value="$40", inline=True)
        embed.set_footer(text="3/19/2024")
        await interation.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(order(bot))